/*
 *   Name: Chih-Ang Wang
 *   AndrewID: chihangw
 */

import java.io.*;
import java.util.*;
import java.io.IOException;

import org.apache.hadoop.io.*;
import org.apache.hadoop.conf.*;
import org.apache.hadoop.util.*;
import org.apache.hadoop.fs.Path;
import org.apache.hadoop.mapred.*;
import org.apache.hadoop.filecache.DistributedCache;

public class WordCount {

    public static class Map extends MapReduceBase implements
                                    Mapper<LongWritable, Text, Text, Text> {

        private String whichFile = "";
        private FileSplit fs = null;
        private Text word = new Text();
        private Text filename = new Text();

        private Set<String> patternsToSkip = new HashSet<String>();

        private void parseSkipFile(Path patternsFile) {
            try {
                /* read in the skip files and store them into hash table */
                BufferedReader f = new BufferedReader(
                                   new FileReader(patternsFile.toString()));
                String skip_ptn = null;
                while ((skip_ptn = f.readLine()) != null) {
                    patternsToSkip.add(skip_ptn);
                }
            } catch (IOException ioe) {
                System.err.println("Exception when Parsing File '" +
                patternsFile + "' : " + StringUtils.stringifyException(ioe));
            }
        }

        public void configure(JobConf conf) {
            Path[] patternsFiles = new Path[0];
            try {
                /* retrieve the skip-words files from the context */
                patternsFiles = DistributedCache.getLocalCacheFiles(conf);
            } catch (IOException ioe) {
                System.err.println("Exception when Parsing File " +
                                    StringUtils.stringifyException(ioe));
            }
            for (Path patternsFile : patternsFiles) {
                /* process each skip-words file */
                parseSkipFile(patternsFile);
            }
        }

        public void map(LongWritable key, Text value, OutputCollector<Text, Text> output,\
                        Reporter reporter) throws IOException {

            /* retrieve the name of file that the key belongs to */
            fs = (FileSplit)reporter.getInputSplit();
            whichFile = fs.getPath().getName() + " ";
            filename.set(whichFile);

            /* process the line for tokenization */
            String line = value.toString();
            line = line.toLowerCase();
            line = line.replaceAll("[^a-z0-9]", " ");

            /* tokenize the string and output the key/value pair */
            StringTokenizer tokenizer = new StringTokenizer(line);

            /* construct the key/value pair */
            while (tokenizer.hasMoreTokens()) {
                String one_word = tokenizer.nextToken();
                if (patternsToSkip.contains(one_word))
                    continue;
                else
                    word.set(one_word);
                    output.collect(word, filename);
            }
        }
    }

    public static class Reduce extends MapReduceBase implements
                                        Reducer<Text, Text, Text, Text> {
        public void reduce(Text key, Iterator<Text> values,
            OutputCollector<Text, Text> output, Reporter reporter) throws IOException {

            String file_list = "";
            TreeMap<String, String> t = new TreeMap<String, String>();

            /* collect file names into a single line */
            while (values.hasNext()) {
                t.put(values.next().toString(), "dummy");
            }
            Set<String> file_sets = t.keySet();

            /* construct the output line */
            for(String file : file_sets ) {
                file_list += file;
            }
            output.collect(key, new Text(file_list));
        }
    }

    public static void main(String[] args) throws Exception {
        JobConf conf = new JobConf(WordCount.class);
        DistributedCache.addCacheFile(new Path("/mnt/english.stop").toUri(), conf);

        conf.setJobName("WordCount");
        conf.set("mapred.textoutputformat.separator", " : ");
        conf.setOutputKeyClass(Text.class);
        conf.setOutputValueClass(Text.class);

        conf.setMapperClass(Map.class);
        conf.setCombinerClass(Reduce.class);
        conf.setReducerClass(Reduce.class);

        conf.setInputFormat(TextInputFormat.class);
        conf.setOutputFormat(TextOutputFormat.class);

        FileInputFormat.setInputPaths(conf, new Path(args[0]));
        FileOutputFormat.setOutputPath(conf, new Path(args[1]));

        JobClient.runJob(conf);
    }
}
