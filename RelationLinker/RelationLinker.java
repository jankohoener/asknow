import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopScoreDocCollector;
import org.apache.lucene.store.FSDirectory;

import java.io.*;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;

/**
 * This terminal application creates an Apache Lucene index in a folder and adds files into this index
 * based on the input of the user.
 * @copyright Adapted from http://www.lucenetutorial.com/sample-apps/textfileindexer-java.html
 * @author Kelvin Tan
 * @author Janko Hoener
 */
public class RelationLinker {
  private static StandardAnalyzer analyzer = new StandardAnalyzer();

  private IndexWriter writer;
  private ArrayList<File> queue = new ArrayList<File>();

  public static void main(String[] args) throws IOException {
	System.out.println("Reading in Lucene index folder and Wikidata data folder...");
	Path LUCENE_INDEX_FOLDER = null;
	Path WIKIDATA_DATA_FOLDER = null;
	RelationLinker indexer = null;
	BufferedReader br = new BufferedReader(
            new InputStreamReader(System.in));
	try {
		if (args.length >= 3) {
			System.out.println("Reading in arguments from command line");
			LUCENE_INDEX_FOLDER = Paths.get(args[1]);
			WIKIDATA_DATA_FOLDER = Paths.get(args[2]);
		}
		else {
			System.out.println("Please give in the location of the Lucene index folder: ");
			String input = br.readLine();
			LUCENE_INDEX_FOLDER = Paths.get(input);
			System.out.println("Please give in the location of the Wikidata data folder: ");
			input = br.readLine();
			WIKIDATA_DATA_FOLDER = Paths.get(input);
		}
		indexer = new RelationLinker(LUCENE_INDEX_FOLDER);
		indexer.indexDirectory(WIKIDATA_DATA_FOLDER);
    } catch (IOException ioe) {
    	System.err.println("Cannot create index, I/O error: " + ioe.getMessage());
    	System.exit(-1);
    }
	catch (Exception e) {
		System.err.println("Cannot create index: " + e.getMessage());
		System.exit(-1);
	}

    indexer.closeIndex();

    IndexReader reader = DirectoryReader.open(FSDirectory.open(LUCENE_INDEX_FOLDER));
    IndexSearcher searcher = new IndexSearcher(reader);

    String query = "";
    while (!query.equalsIgnoreCase("q")) {
      try {
        System.out.println("Enter the search query (q=quit):");
        query = br.readLine();
        if (query.equalsIgnoreCase("q")) {
          break;
        }
        TopScoreDocCollector collector = TopScoreDocCollector.create(5);
        Query q = new QueryParser("contents", analyzer).parse(query);
        searcher.search(q, collector);
        ScoreDoc[] hits = collector.topDocs().scoreDocs;

        for(int i=0;i<hits.length;++i) {
          int docId = hits[i].doc;
          Document d = searcher.doc(docId);
          System.out.println((i + 1) + ". " + d.get("filename") + " score=" + hits[i].score);
        }

      } catch (Exception e) {
        System.out.println("Error searching " + query + " : " + e.getMessage());
      }
    }

  }

  /**
   * Constructor
   * @param indexDir the name of the folder in which the index should be created
   * @throws java.io.IOException when exception creating index.
   */
  RelationLinker(Path indexFolder) throws IOException {
    FSDirectory dir = FSDirectory.open(indexFolder);


    IndexWriterConfig config = new IndexWriterConfig(analyzer);

    writer = new IndexWriter(dir, config);
  }

  /**
   * Indexes a directory
   * @param dataFolder the Path object of the data folder we wish to add to the index
   * @throws java.io.IOException when exception
   */
  public void indexDirectory(Path dataFolder) throws IOException {
    //gets the list of files in the folder 
    addFiles(dataFolder.toFile());
   
    for (File f : queue) {
      FileReader fr = null;
      try {
        Document doc = new Document();

        //===================================================
        // add contents of file
        //===================================================
        fr = new FileReader(f);
        doc.add(new TextField("contents", fr));
        doc.add(new StringField("path", f.getPath(), Field.Store.YES));
        doc.add(new StringField("filename", f.getName(), Field.Store.YES));

        writer.addDocument(doc);
        System.out.println("Added: " + f);
      } catch (Exception e) {
        System.out.println("Could not add: " + f);
      } finally {
        fr.close();
      }
    }
   
    int newNumDocs = writer.numDocs();
    System.out.println("");
    System.out.println("************************");
    System.out.println(newNumDocs  + " documents added.");
    System.out.println("************************");

    queue.clear();
  }

  private void addFiles(File file) {

    if (!file.exists()) {
      System.err.println(file + " does not exist.");
    }
    if (file.isDirectory()) {
      for (File f : file.listFiles()) {
        addFiles(f);
      }
    } else {
      String filename = file.getName().toLowerCase();
      //===================================================
      // Only index text files
      //===================================================
      if (filename.endsWith(".htm") || filename.endsWith(".html") ||
              filename.endsWith(".xml") || filename.endsWith(".txt")) {
        queue.add(file);
      } else {
        System.out.println("Skipped " + filename);
      }
    }
  }

  /**
   * Close the index.
   * @throws java.io.IOException when exception closing
   */
  public void closeIndex() throws IOException {
    writer.close();
  }
}