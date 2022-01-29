# Scalafix rules for scalafix

To develop rule:
```
sbt ~tests/test
# edit rules/src/main/scala/fix/Scalafix.scala
```
To Enable scala fix in a project, add the following:

--> project/plugins.sbt 
addSbtPlugin("ch.epfl.scala" % "sbt-scalafix" % "0.9.34")

--> build.sbt

ThisBuild / scalafixDependencies +=
"com.cloudknox" %% "scalafix" % "0.0.1-SNAPSHOT"

lazy val myproject = project.settings(
scalaVersion := "2.12.13", // 2.11.12, or 2.13.8
addCompilerPlugin(scalafixSemanticdb), // enable SemanticDB
scalacOptions ++= List(
"-Yrangepos",          // required by SemanticDB compiler plugin
"-Ywarn-unused-import" // required by `RemoveUnused` rule
)
)

In sbt shell, do: 

[project] $ scalafixEnable
[project] $ scalafix AddContextVarV1

The last one is to run the specific rule on a project
