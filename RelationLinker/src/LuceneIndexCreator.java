import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StringField;
import org.apache.lucene.document.TextField;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.store.FSDirectory;

/**
 * 
 */

/** This application creates a Lucene index from a file or directory.
 * @copyright Adapted from http://www.lucenetutorial.com/sample-apps/textfileindexer-java.html
 * @author Kelvin Tan
 * @author Janko Hoener
 *
 */
public class LuceneIndexCreator {
	  private ArrayList<File> queue = new ArrayList<File>();
	  private IndexWriter writer;
	  private static StandardAnalyzer analyzer = new StandardAnalyzer();

	/**
	 * @param args
	 * @throws IOException 
	 */
	public static void main(String[] args) throws IOException{
		System.out.println("Reading in Lucene index folder and Wikidata data folder...");
		Path LUCENE_INDEX_FOLDER = null;
		Path WIKIDATA_DATA_FOLDER = null;
		LuceneIndexCreator indexer = null;
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
			indexer = new LuceneIndexCreator(LUCENE_INDEX_FOLDER);
			indexer.indexFileOrDirectory(WIKIDATA_DATA_FOLDER);
	    } catch (IOException ioe) {
	    	System.err.println("Cannot create index, I/O error: " + ioe.getMessage());
	    	System.exit(-1);
	    }
		catch (Exception e) {
			System.err.println("Cannot create index: " + e.getMessage());
			System.exit(-1);
		}

	    indexer.closeIndex();
	}
	
	  /**
	   * Constructor
	   * @param indexDir the name of the folder in which the index should be created
	   * @throws java.io.IOException when exception creating index.
	   */
	  LuceneIndexCreator(Path indexFolder) throws IOException {
	    FSDirectory dir = FSDirectory.open(indexFolder);


	    IndexWriterConfig config = new IndexWriterConfig(analyzer);

	    writer = new IndexWriter(dir, config);
	  }
	  
	  /**
	   * Close the index.
	   * @throws java.io.IOException when exception closing
	   */
	  public void closeIndex() throws IOException {
	    writer.close();
	  }
	  /**
	   * Indexes a file or directory
	   * @param dataFile the Path object of the data folder we wish to add to the index
	   * @throws java.io.IOException when exception
	   */
	  public void indexFileOrDirectory(Path dataFile) throws IOException {
	    //gets the list of files in the folder 
	    addFiles(dataFile.toFile());
	   
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

}
