<ol>
	<% 
	String n_in = request.getParameter("n");
	int n = Integer.parseInt(n_in);
	for (int i = 0; i < n; i++) {
		out.println("<li>");
		if ((i % 3) == 0) {
			out.println("Fizz");
		}
		if ((i % 5)  == 0) {
			out.println("Buzz");
		}
		if ((i % 3) != 0 && (i % 5) != 0) {
			out.println(n_in);
		}
		out.println("</li>");
	}
	%>
</ol>