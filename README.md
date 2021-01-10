# HttpServer

This repository contains code that is very inefficient, bit unstructured. Its essentially a noobs attempt at reinventing the wheel. Yet it exists and is super useful to get a strong intuition of how web frameworks (the wheel) work under the hood. Wearing a developers hat really helps in appreciating the plethora of tools out there. It also help one to learn to deploy them quickly with minimal effort.

## Summary
First step is to create a server that can hendle all the website related requests by a browser. High level view of this process:
- This server talks/listens via a __socket__ which has a port number and an ip address. The socket 'listens' to any incoming request nested under an infinite while loop. It binds itself to one client and serves various requests send subsequently. 
- Each of these requests are binary representations of strings. Now, these strings could be anything but that would make most of these unintelligible to the server. No surprise, there is a standard format : __HTTP__ that is followed throughout web, a global language. 
- After establishing this common language, some common rules for semantics are also standardized: for example, a client (mostly a web browser) is capable of rendering __HTML__ into a website. This is another sub language in the semantics domain. This step involves creating some __HTML__ formatted text sent as a payload of the global language __HTTP__. This string is created using __Jinja2__ library which can programaticaly populate some pre-written templates and render them as text.
- Next is to map the various client requests to the resources available and return them (this is the main JD of the server). A python class handles this mapping.  


# How the WEB works:

## TCP/IP communications model:

## Socket Programming:

## What is HTTP:

## General Code optimizations:

### Multi-threading


