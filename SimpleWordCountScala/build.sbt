name := "spark-wordcount"

version := "1.0"

scalaVersion := "2.12.10"
val sparkVersion = "3.2.0"


libraryDependencies += "org.apache.spark" %% "spark-core" % sparkVersion
