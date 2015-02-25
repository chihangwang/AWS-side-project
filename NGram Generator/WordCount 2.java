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
import org.apache.hadoop.mapreduce.*;
import org.apache.hadoop.mapreduce.lib.input.FileInputFormat;
import org.apache.hadoop.mapreduce.lib.input.TextInputFormat;
import org.apache.hadoop.mapreduce.lib.output.FileOutputFormat;
import org.apache.hadoop.mapreduce.lib.output.TextOutputFormat;

public class WordCount {

    public static class Map extends Mapper<LongWritable, Text, Text, LongWritable> {

        private Text word = new Text();
        private final static LongWritable one = new LongWritable(1);

        public ArrayList<String> generateNGram(String [] tokens, int N) {

            int num_of_tokens = tokens.length;
            ArrayList<String> output = new ArrayList<String>();

            if (num_of_tokens < N)
                return output;

            for (int i=0; i<= num_of_tokens - N; i++) {

                String gram = "";
                for (int j=0; j<N; j++) {
                    gram += tokens[i+j] + " ";
                }
                output.add(gram.trim());

            }
            return output;
        }

        public void map(LongWritable key, Text value, Context context)
        throws IOException, InterruptedException {

            /* process the line for tokenization */
            String line = value.toString();
            line = line.toLowerCase();
            line = line.replaceAll("[^a-z]", " ");

            /* tokenize and construct n-gram string */
            ArrayList<String> tokenList = new ArrayList<String>();
            StringTokenizer tokenizer = new StringTokenizer(line);
            while (tokenizer.hasMoreTokens()) {
                tokenList.add(tokenizer.nextToken());
            }
            Integer size = tokenList.size();
            String [] tokens = tokenList.toArray(new String[size]);

            /* construct 1-gram to 5-gram and print out line */
            for (int i=1; i<=5; i++) {

                ArrayList<String> temp = generateNGram(tokens, i);
                Integer cnt = temp.size();
                String [] ngrams = temp.toArray(new String[cnt]);

                if(ngrams.length == 0)
                    continue;
                for (String ngram : ngrams) {
                    word.set(ngram);
                    context.write(word, one);
                }
            }
        }
    }

    public static class Reduce extends Reducer<Text, LongWritable, Text, LongWritable> {

        public void reduce(Text key, Iterable<LongWritable> values, Context context)
        throws IOException, InterruptedException {
            long sum = 0;
            for (LongWritable val : values) {
                sum += val.get();
            }
            context.write(key, new LongWritable(sum));
        }
    }

    public static void main(String[] args) throws Exception {

        Configuration conf = new Configuration();

        Job job = new Job(conf, "WordCount");
        job.setJarByClass(WordCount.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(LongWritable.class);

        job.setMapperClass(Map.class);
        job.setReducerClass(Reduce.class);

        job.setInputFormatClass(TextInputFormat.class);
        job.setOutputFormatClass(TextOutputFormat.class);

        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));
        job.waitForCompletion(true);

    }
}
