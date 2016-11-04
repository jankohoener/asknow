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

import java.util.regex.Pattern;

// [START example]
@SuppressWarnings("serial")
public class SignUpServlet extends HttpServlet {
	
  public void print_error (PrintWriter out, String error) throws IOException {
  	  out.format("<span style='color: red'>%s</span>", error);
  }
  
  public void print_break (PrintWriter out) throws IOException {
  	  out.println("<br>");
  }
	
  public void write_form (HttpServletResponse resp, String username, String email, int errors) throws IOException {
  
  	resp.setHeader("Content-Type", "text/html");
    PrintWriter out = resp.getWriter();
    out.println("<form method='post'>");
    out.format("<label>Username<input name='username' value='%s'></label>", username);
    if ((errors & 1) > 0) {
    	print_error(out, "That's an invalid username!");
    }
    print_break(out);
    out.println("<label>Password <input type='password' name='password'></label>");
    if ((errors & 2) > 0) {
    	print_error(out, "That's an invalid password!");
    }
    print_break(out);
    out.println("<label>Verify password <input type='password' name='verify'></label>");
    if ((errors & 4) > 0) {
    	print_error(out, "The passwords don't match!");
    }
    print_break(out);
    out.format("<label>Email (optional) <input name='email' value='%s'></label>", email);
    if ((errors & 8) > 0) {
    	print_error(out, "That's an invalid email!");
    }
    print_break(out);
    out.println("<input type='submit'>");
    out.println("</form>");
  }
  
  public void write_form(HttpServletResponse resp) throws IOException {
  	write_form(resp, "", "", 0);
  }
  
  public String escape_html (String input) {
  	  return input.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\"", "&quot;");
  }

  @Override
  public void doGet(HttpServletRequest req, HttpServletResponse resp) throws IOException {
  	write_form(resp);
  }
  
  public void doPost(HttpServletRequest req, HttpServletResponse resp) throws IOException {
  	  resp.setHeader("Content-Type", "text/html");
  	  String username = req.getParameter("username");
  	  String password = req.getParameter("password");
  	  String verify = req.getParameter("verify");
  	  String email = req.getParameter("email");
  	  
  	  boolean validusername = Pattern.matches("^[a-zA-Z0-9_-]{3,20}$", username);
  	  boolean validpassword = Pattern.matches("^.{3,20}$", password);
  	  boolean passwordsmatch = password.equals(verify);
  	  boolean validemail = Pattern.matches("^[\\S]+@[\\S]+.[\\S]+$", email) || email.equals("");
  	  
  	  if (validusername && validpassword && passwordsmatch && validemail) {
  	  	  resp.setStatus(303);
  	  	  resp.sendRedirect("/welcome?username=" + username);
  	  }
  	  else {
  	  	  int errors = 0;
  	  	  if (!validusername) {
  	  	  	  errors += 1;
  	  	  }
  	  	  if (!validpassword) {
  	  	  	  errors += 2;
  	  	  }
  	  	  if (!passwordsmatch) {
  	  	  	  errors += 4;
  	  	  }
  	  	  if (!validemail) {
  	  	  	  errors += 8;
  	  	  }
  	  	  write_form(resp, escape_html(username), escape_html(email), errors);
  	  }
  	
  }
}
// [END example]
