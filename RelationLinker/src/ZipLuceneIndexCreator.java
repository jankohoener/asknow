import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Enumeration;
import java.util.Scanner;
import java.util.zip.GZIPInputStream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;

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
public class ZipLuceneIndexCreator {
	private IndexWriter writer;
	private static StandardAnalyzer analyzer = new StandardAnalyzer();

	/**
	 * @param args
	 * @throws IOException 
	 */
	public static void main(String[] args) throws IOException{
		System.out.println("Reading in Lucene index folder and Wikidata data folder...");
		Path LUCENE_INDEX_FOLDER = null;
		String ZIP_FILE_NAME = "";
		ZipLuceneIndexCreator indexer = null;
		BufferedReader br = new BufferedReader(
				new InputStreamReader(System.in));
		try {
			if (args.length >= 3) {
				System.out.println("Reading in arguments from command line");
				LUCENE_INDEX_FOLDER = Paths.get(args[1]);
				ZIP_FILE_NAME = args[2];
			}
			else {
				System.out.println("Please give in the location of the Lucene index folder: ");
				String input = br.readLine();
				LUCENE_INDEX_FOLDER = Paths.get(input);
				System.out.println("Please give in the location of the Wikidata data folder: ");
				input = br.readLine();
				ZIP_FILE_NAME = input.replaceAll("\n", "");
			}
			indexer = new ZipLuceneIndexCreator(LUCENE_INDEX_FOLDER);
			indexer.indexFileOrDirectory(ZIP_FILE_NAME);
		} catch (IOException ioe) {
			System.err.println("Cannot create index, I/O error: " + ioe.getMessage());
			System.exit(-1);
		}
		catch (Exception e) {
			System.err.println("Cannot create index: " + e.getMessage());
			System.exit(-1);
		}

		indexer.closeIndex();
		System.out.println("Index successfully created.");
	}

	/**
	 * Constructor
	 * @param indexDir the name of the folder in which the index should be created
	 * @throws java.io.IOException when exception creating index.
	 */
	ZipLuceneIndexCreator(Path indexFolder) throws IOException {
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
	public void indexFileOrDirectory(String zipFileName) throws IOException {

		InputStream in = new GZIPInputStream(new FileInputStream(zipFileName));
		Scanner sc = new Scanner(in);
		while (sc.hasNext()) {
			String curLine = sc.nextLine();
			if (curLine.startsWith("#")) {
				continue; // ignore comments
			}
			String subject, predicate, object;
			String[] curLineParts = curLine.split("\\s+");
			if (curLineParts.length >= 3) {
				subject = curLineParts[0];
				predicate = curLineParts[1];
				object = curLineParts[2];
			}
			else {
				continue;
			}
			
			Document doc = new Document();
			doc.add(new TextField("subject", subject, Field.Store.YES));
			doc.add(new TextField("predicate", predicate, Field.Store.YES));
			doc.add(new TextField("object", object, Field.Store.YES));
			writer.addDocument(doc);
		}

		/*byte[] buffer = new byte[65536];
		int noRead;
		while ((noRead = in.read(buffer)) != -1) {
			String bytestr = new String(buffer);
			System.out.println("***** BYTESTRING *****");
			System.out.println(bytestr);
			System.out.println("***** END *****");
			//System.out.write(buffer, 0, noRead);
			//Document doc = new Document();
		}*/
		in.close();

		/*ZipFile zipFile = new ZipFile(zipFileName);

		Enumeration<? extends ZipEntry> entries = zipFile.entries();

		while(entries.hasMoreElements()){
			ZipEntry entry = entries.nextElement();
			InputStream stream = zipFile.getInputStream(entry);
			System.out.println(stream.toString());
		}

		zipFile.close();
		 */
		/*
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


		int newNumDocs = writer.numDocs();
		System.out.println("");
		System.out.println("************************");
		System.out.println(newNumDocs  + " documents added.");
		System.out.println("************************");
		 */
	}


}
