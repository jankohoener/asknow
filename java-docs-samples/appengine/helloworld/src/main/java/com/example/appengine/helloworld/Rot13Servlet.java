/**
 * Copyright 2015 Google Inc. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.example.appengine.helloworld;

import java.io.IOException;
import java.io.PrintWriter;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

// [START example]
@SuppressWarnings("serial")
public class Rot13Servlet extends HttpServlet {
	
  public void write_form (HttpServletResponse resp, String textcontent) throws IOException {
  	resp.setHeader("Content-Type", "text/html");
    PrintWriter out = resp.getWriter();
    out.println("<h1>Rot 13 Servlet</h1>");
    out.format("<form method='post' action='/rot13'><textarea name='text'>%s</textarea><input type='submit'></form>", textcontent);
  }
  
  public String rot13 (String input) {
  	  StringBuilder rot13 = new StringBuilder(input);
  	  for (int i = 0; i < input.length(); i++) {
  	  	  if (input.charAt(i) >= 'a' && input.charAt(i) <= 'z') {
  	  	  	  int newchar = (int)input.charAt(i);
  	  	  	  newchar -= ((int)'a');
  	  	  	  newchar += 13;
  	  	  	  newchar %= 26;
  	  	  	  newchar += ((int)'a');
  	  	  	  rot13.setCharAt(i, (char)newchar);
  	  	  }
  	  	  if (input.charAt(i) >= 'A' && input.charAt(i) <= 'Z') {
  	  	  	  int newchar = (int)input.charAt(i);
  	  	  	  newchar -= ((int)'A');
  	  	  	  newchar += 13;
  	  	  	  newchar %= 26;
  	  	  	  newchar += ((int)'A');
  	  	  	  rot13.setCharAt(i, (char)newchar);
  	  	  }
  	  }
  	  return rot13.toString();
  }
  
  public String escape_html (String input) {
  	  return input.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;");
  }

  @Override
  public void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
    write_form(resp, "");
  }
  
  @Override
  public void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException {
  	  String input = req.getParameter("text");
  	  input = rot13(input);
  	  input = escape_html(input);
  	  write_form(resp, input);
  }
}
// [END example]
