import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.file.Path;
import java.nio.file.Paths;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.DirectoryReader;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryparser.classic.ParseException;
import org.apache.lucene.queryparser.classic.QueryParser;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopScoreDocCollector;
import org.apache.lucene.store.FSDirectory;

/**
 * 
 */

/**
 * @author Janko Hoener
 *
 */
public class LuceneIndexSearcher {

	private static StandardAnalyzer analyzer = new StandardAnalyzer();
	private IndexSearcher searcher;


	public LuceneIndexSearcher(Path LUCENE_INDEX_FOLDER) throws IOException {
		IndexReader reader = DirectoryReader.open(FSDirectory.open(LUCENE_INDEX_FOLDER));
		searcher = new IndexSearcher(reader);
	}


	public static void main(String[] args) throws IOException {
		System.out.println("Reading in Lucene index folder and Wikidata data folder...");
		Path LUCENE_INDEX_FOLDER = null;
		BufferedReader br = new BufferedReader(
				new InputStreamReader(System.in));
		if (args.length >= 2) {
			System.out.println("Reading in arguments from command line");
			LUCENE_INDEX_FOLDER = Paths.get(args[1]);
		}
		else {
			System.out.println("Please give in the location of the Lucene index folder: ");
			String input = br.readLine();
			LUCENE_INDEX_FOLDER = Paths.get(input);
		}
		LuceneIndexSearcher indexer = new LuceneIndexSearcher(LUCENE_INDEX_FOLDER);

		String query = "";
		while (!query.equalsIgnoreCase("q")) {
			try {
				System.out.println("Enter the search query (q=quit):");
				query = br.readLine();
				if (query.equalsIgnoreCase("q")) {
					break;
				}
				ScoreDoc[] hits = indexer.getHits(query);
				indexer.printHits(hits);
			} catch (Exception e) {
				System.out.println("Error searching " + query + " : " + e.getMessage());
			}
		}

	}


	private void printHits(ScoreDoc[] hits) throws IOException {
		for(int i=0;i<hits.length;++i) {
			int docId = hits[i].doc;
			Document d = searcher.doc(docId);
			System.out.println((i + 1) + ". " + d.get("filename") + " score=" + hits[i].score);
		}

	}


	private ScoreDoc[] getHits(String query) throws ParseException, IOException {
		TopScoreDocCollector collector = TopScoreDocCollector.create(5);
		Query q = new QueryParser("contents", analyzer).parse(query);
		searcher.search(q, collector);
		return collector.topDocs().scoreDocs;
	}

}
