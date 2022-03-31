import org.apache.spark.SparkContext
import org.apache.spark.SparkConf

object MainClass{
    def main(args: Array[String]){

        val conf = new SparkConf().setAppName("appName")
        val sc = new SparkContext(conf)

        val inputPath = args(0)
        val outputPath = args(1)
        
        val textFile = sc.textFile(inputPath)
        val counts = textFile.flatMap(line => line.split(" ").filter(line => line.matches("[A-Za-z]+[,:;!\\.\\?-]+")))
                         .map(word => (word, 1))
                         .reduceByKey(_ + _)
                         .map(p => (p._2,  p._1))
                         .sortByKey(false, 1)
                         .map(p => s"${p._1} ${p._2}")
        counts.saveAsTextFile(outputPath)
    }
}
