Install the Lucene Index in Java as well as `ant` as described here: https://lucene.apache.org/core/downloads.html

Then open these files in Eclipse.

Open a terminal and `cd` to the extracted Lucene directory. Run the following commands for each $dir in {queryparser, core, analysis/common/}.
At the end of each output, there's a path to a build JAR file. Link this file in Eclipse with this project (via File -> Properties -> Java Build Path -> Libraries -> Add external JARs).
```
  cd $dir
  ant
  cd
  ```

You can run the files via Eclipse's Run function.
