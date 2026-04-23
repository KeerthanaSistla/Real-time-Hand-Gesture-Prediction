from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import StructType, StringType, DoubleType

# Spark session
spark = SparkSession.builder \
    .appName("GestureAnalytics") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Schema of incoming JSON
schema = StructType() \
    .add("gesture", StringType()) \
    .add("confidence", DoubleType()) \
    .add("timestamp", DoubleType())

# Read from Kafka
df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "gesture_topic") \
    .load()

# Convert binary -> string -> JSON
json_df = df.selectExpr("CAST(value AS STRING)")

parsed_df = json_df.select(
    from_json(col("value"), schema).alias("data")
).select("data.*")

# Print output
query = parsed_df.writeStream \
    .format("console") \
    .outputMode("append") \
    .option("truncate", False) \
    .option("checkpointLocation", "/tmp/gesture_checkpoint") \
    .start()

query.awaitTermination()