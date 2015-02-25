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

import org.apache.hadoop.hbase.client.Delete;
import org.apache.hadoop.hbase.client.Get;
import org.apache.hadoop.hbase.client.HBaseAdmin;
import org.apache.hadoop.hbase.client.HTable;
import org.apache.hadoop.hbase.client.Result;
import org.apache.hadoop.hbase.client.ResultScanner;
import org.apache.hadoop.hbase.client.Scan;
import org.apache.hadoop.hbase.client.Put;
import org.apache.hadoop.hbase.HBaseConfiguration;
import org.apache.hadoop.hbase.HColumnDescriptor;
import org.apache.hadoop.hbase.HTableDescriptor;
import org.apache.hadoop.hbase.KeyValue;
import org.apache.hadoop.hbase.MasterNotRunningException;
import org.apache.hadoop.hbase.ZooKeeperConnectionException;
import org.apache.hadoop.hbase.util.Bytes;

public class WordCount {

    private static HTable table = null;
    private static String tableName = "TextPredictorTable";
    private static String columnFamily = "TextProbability";

    // helper for hbase PUT operation
    public static void addRecordHBase(String tableName, String rowKey,
        String family, String qualifier, String value) throws Exception {

        try {
            Put put = new Put(Bytes.toBytes(rowKey));
            put.add(Bytes.toBytes(family), Bytes.toBytes(qualifier), Bytes.toBytes(value));
            table.put(put);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static class Map extends Mapper<LongWritable, Text, Text, Text> {

        private Text KEY = new Text();
        private Text VAL = new Text();

        public void map(LongWritable key, Text value, Context context)
        throws IOException, InterruptedException {

            /* take input string from the previous ngram results */
            String line = value.toString().trim();

            /* split line into tokens*/
            ArrayList<String> tokenList = new ArrayList<String>();
            StringTokenizer tokenizer = new StringTokenizer(line);
            while (tokenizer.hasMoreTokens()) {
                tokenList.add(tokenizer.nextToken());
            }
            Integer size = tokenList.size();

            /* if it's 1-gram, simply ignore */
            if (size <= 2)
                return;

            /* construct the <k, v>=<key="non-last", val="last-count"> */
            String [] tokens = tokenList.toArray(new String[size]);
            String keyOut = "", val="";
            for (int i=0; i<size; i++) {

                keyOut += tokens[i] + " ";

                if (i == size-3) {
                    keyOut = keyOut.trim();
                    val = tokens[i+1] + "_" + tokens[i+2];
                    break;
                }
            }

            /* output for reducer */
            KEY.set(keyOut);
            VAL.set(val);
            context.write(KEY, VAL);
        }
    }

    public static class Reduce extends Reducer<Text, Text, Text, Text> {

        public void reduce(Text key, Iterable<Text> values, Context context)
        throws IOException, InterruptedException {

            HashMap<String, Long> hm = new HashMap<String, Long>();
            long sum = 0;

            // store in hashmap for sorting
            for (Text val : values) {
                String [] parts = val.split("_");
                String word = parts[0];
                long   cnt  = Long.parseLong(parts[1], 10);
                sum += cnt
                hm.put(word, cnt);
            }

            TreeMap<String, Long> sortedMap = getSortedMapFromUnsortedMap(hm);
            int i = 0;
            int MAX_CNT = 5;

            // calculate the probability based on the top 5 words
            for (String hashKey: sortedMap.keySet())
            {
                if (++i > MAX_CNT) {
                    break;
                }

                // calculate probability for each word
                float prob = (float)hm.get(hashKey) / (float)sum;
                // sort in reverse order
                prob = (float)1.0 - prob;

                // insert data into hbase
                addRecordHBase(tableName, key.toString(), columnFamily, Float.toString(prob), hashKey);
            }
        }

        // helper function to sort the map based on value
        private static TreeMap<String, Long> getSortedMapFromUnsortedMap(HashMap<String, Long> map) {

            HashValueComparator hvc =  new HashValueComparator(map);
            TreeMap<String, Long> sortedTreeMap = new TreeMap<String, Long>(hvc);
            sortedTreeMap.putAll(map);
            return sortedTreeMap;

        }
    }

    public static void main(String[] args) throws Exception {

        // init the hbase
        Configuration hbconf = HBaseConfiguration.create();
        HBaseAdmin admin = new HBaseAdmin(hbconf);
        HTableDescriptor tableDesc = new HTableDescriptor(tableName);
        tableDesc.addFamily(new HColumnDescriptor(columnFamily);
        admin.createTable(tableDesc);
        table = new HTable(hbconf, tableName);

        // init the hadoop
        Configuration hdconf = new Configuration();
        Job job = new Job(hdconf, "WordCount");
        job.setJarByClass(WordCount.class);
        job.setOutputKeyClass(Text.class);
        job.setOutputValueClass(Text.class);

        job.setMapperClass(Map.class);
        job.setReducerClass(Reduce.class);

        job.setInputFormatClass(TextInputFormat.class);
        job.setOutputFormatClass(TextOutputFormat.class);

        FileInputFormat.addInputPath(job, new Path(args[0]));
        FileOutputFormat.setOutputPath(job, new Path(args[1]));
        job.waitForCompletion(true);

    }
}
