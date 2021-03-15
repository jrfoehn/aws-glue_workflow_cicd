import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, ['JOB_NAME', 'bucket'])
bucket=args['bucket']
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)
## @type: DataSource
## @args: [database = "nyc_db", table_name = "csv_trip_data", transformation_ctx = "datasource0"]
## @return: datasource0
## @inputs: []
datasource0 = glueContext.create_dynamic_frame.from_catalog(database = "nyc_db", table_name = "csv_trip_data", transformation_ctx = "datasource0")
## @type: ApplyMapping
## @args: [mapping = [("vendor_id", "string", "vendor_id", "string"), ("pickup_datetime", "string", "pickup_datetime", "string"), ("dropoff_datetime", "string", "dropoff_datetime", "string"), ("passenger_count", "long", "passenger_count", "long"), ("trip_distance", "string", "trip_distance", "string"), ("pickup_longitude", "string", "pickup_longitude", "string"), ("pickup_latitude", "string", "pickup_latitude", "string"), ("rate_code", "long", "rate_code", "long"), ("store_and_fwd_flag", "string", "store_and_fwd_flag", "string"), ("dropoff_longitude", "string", "dropoff_longitude", "string"), ("dropoff_latitude", "string", "dropoff_latitude", "string"), ("payment_type", "string", "payment_type", "string"), ("fare_amount", "double", "fare_amount", "double"), ("surcharge", "double", "surcharge", "double"), ("mta_tax", "double", "mta_tax", "double"), ("tip_amount", "string", "tip_amount", "string"), ("tolls_amount", "double", "tolls_amount", "double"), ("total_amount", "double", "total_amount", "double"), ("vendorid", "long", "vendorid", "long"), ("tpep_pickup_datetime", "string", "tpep_pickup_datetime", "string"), ("tpep_dropoff_datetime", "string", "tpep_dropoff_datetime", "string"), ("ratecodeid", "long", "ratecodeid", "long"), ("extra", "double", "extra", "double"), ("improvement_surcharge", "double", "improvement_surcharge", "double"), ("pulocationid", "long", "pulocationid", "long"), ("dolocationid", "long", "dolocationid", "long"), ("congestion_surcharge", "double", "congestion_surcharge", "double")], transformation_ctx = "applymapping1"]
## @return: applymapping1
## @inputs: [frame = datasource0]
applymapping1 = ApplyMapping.apply(frame = datasource0, mappings = [("vendor_id", "string", "vendor_id", "string"), ("pickup_datetime", "string", "pickup_datetime", "string"), ("dropoff_datetime", "string", "dropoff_datetime", "string"), ("passenger_count", "long", "passenger_count", "long"), ("trip_distance", "string", "trip_distance", "string"), ("pickup_longitude", "string", "pickup_longitude", "string"), ("pickup_latitude", "string", "pickup_latitude", "string"), ("rate_code", "long", "rate_code", "long"), ("store_and_fwd_flag", "string", "store_and_fwd_flag", "string"), ("dropoff_longitude", "string", "dropoff_longitude", "string"), ("dropoff_latitude", "string", "dropoff_latitude", "string"), ("payment_type", "string", "payment_type", "string"), ("fare_amount", "double", "fare_amount", "double"), ("surcharge", "double", "surcharge", "double"), ("mta_tax", "double", "mta_tax", "double"), ("tip_amount", "string", "tip_amount", "string"), ("tolls_amount", "double", "tolls_amount", "double"), ("total_amount", "double", "total_amount", "double"), ("vendorid", "long", "vendorid", "long"), ("tpep_pickup_datetime", "string", "tpep_pickup_datetime", "string"), ("tpep_dropoff_datetime", "string", "tpep_dropoff_datetime", "string"), ("ratecodeid", "long", "ratecodeid", "long"), ("extra", "double", "extra", "double"), ("improvement_surcharge", "double", "improvement_surcharge", "double"), ("pulocationid", "long", "pulocationid", "long"), ("dolocationid", "long", "dolocationid", "long"), ("congestion_surcharge", "double", "congestion_surcharge", "double")], transformation_ctx = "applymapping1")
## @type: ResolveChoice
## @args: [choice = "make_struct", transformation_ctx = "resolvechoice2"]
## @return: resolvechoice2
## @inputs: [frame = applymapping1]
resolvechoice2 = ResolveChoice.apply(frame = applymapping1, choice = "make_struct", transformation_ctx = "resolvechoice2")
## @type: DropNullFields
## @args: [transformation_ctx = "dropnullfields3"]
## @return: dropnullfields3
## @inputs: [frame = resolvechoice2]
dropnullfields3 = DropNullFields.apply(frame = resolvechoice2, transformation_ctx = "dropnullfields3")
## @type: DataSink
## @args: [connection_type = "s3", connection_options = {"path": f"s3://{bucket}/parquet/"}, format = "parquet", transformation_ctx = "datasink4"]
## @return: datasink4
## @inputs: [frame = dropnullfields3]
datasink4 = glueContext.write_dynamic_frame.from_options(frame = dropnullfields3, connection_type = "s3", connection_options = {"path": f"s3://{bucket}/parquet/"}, format = "parquet", transformation_ctx = "datasink4")
job.commit()