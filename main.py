import json
import urllib
import cgi
from os.path import isfile, join
from os import listdir
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import urlparse, parse_qs
import mimetypes

mimetypes.init()
                    
                    
class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == '/list':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            files = [f for f in listdir('.') if isfile(join('.',f))]
            self.wfile.write(json.dumps(files))
            return
        elif url.path == '/get':
            queryParams = parse_qs(url.query)
            if "file" in queryParams and len(queryParams["file"]):
                fileName = urllib.unquote(queryParams["file"][0])
                filePath = join('.',fileName)
                if isfile(filePath):
                    mime = mimetypes.guess_type(filePath)[0]
                    self.send_response(200)
                    self.send_header('Content-type', mime or 'application/octet-stream')
                    self.send_header('Content-Disposition', 'attachment; filename=' + fileName)
                    self.end_headers()
                    
                    with open(join('.',fileName)) as f:
                        self.wfile.write(f.read())
                    return
                else:
                    self.send_response(404)
            else:
                self.send_response(404)
        elif url.path == "/":
            self.send_response(200)
            self.wfile.write(HTML)
        else:
            self.send_response(404)

    def do_POST(self):
        if self.path == '/upload':
            form = cgi.FieldStorage(fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST'})
            #Assuming the content-type is multipart
            print "processing upload:", form["file"].filename
            if "file" in form:
                with open(form["file"].filename, "wb") as out:
                    out.write(form["file"].value)
                self.send_response(200)
                return
        self.send_response(404)

def main():
    server = HTTPServer(('', 8080), RequestHandler)
    server.serve_forever()
    






HTML= '''

<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Bootstrap 3, from LayoutIt!</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="">
  <meta name="author" content="">

	<link href="//netdna.bootstrapcdn.com/bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">
    <link href="//cdnjs.cloudflare.com/ajax/libs/dropzone/3.7.1/css/dropzone.min.css" rel="stylesheet">
	<script type="text/javascript" src="//code.jquery.com/jquery-1.10.2.min.js"></script>
	<script type="text/javascript" src="//netdna.bootstrapcdn.com/bootstrap/3.0.3/js/bootstrap.min.js"></script>
    <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/dropzone/3.7.1/dropzone.js"></script>
</head>

<body>
<div class="container">
	<div class="row clearfix">
		<div class="col-md-2 column">
		</div>
		<div class="col-md-5 column" id="divFileList">
		</div>
		<div class="col-md-5 column dropzone dz-clickable" id="divDropZone">
		</div>
	</div>
</div>
<script>
$.ajax({
    type: "GET",
    url: "/list",
    success: function (data) {
        var htmlStr = data.map(function(x){ return '<li><a href="/get?file=' + encodeURIComponent(x) + '">' + x + '</a></li>'; }).join("\\n");
        $('#divFileList').html(htmlStr);
    }
})
$("#divDropZone").dropzone({ url: "/upload" });
</script>
</body>
</html>



'''


if __name__ == '__main__':
    main()