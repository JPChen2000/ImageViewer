import os
import sys
import json
import http.server
import socketserver
from urllib.parse import unquote

PORT = 8080
PATH = "./"
# 定义一个继承自http.server.SimpleHTTPRequestHandler的类
class ImageRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers['Content-Length'])

            # 读取请求体中的数据
            post_data = self.rfile.read(content_length)

            # 将数据解析为字典
            data = json.loads(post_data)

            # 在控制台打印收到的数据
            print("Received POST data:", data)

            if data['action'] == "save":
                path = data['path']
                if len(path) == 0:
                    status = 'error'
                else:
                    imgs = data['imgs']
                    with open(path, "w") as f:
                        for path in imgs:
                            f.write("{}\n".format(path))
                    status = 'success'
            elif data['action'] == "delete":
                imgs = data['imgs']
                for img in imgs:
                    os.remove(img)
                status = 'success'
            else:
                status = 'error'
                    
            if status == 'success': 
                self.send_response(200)
            else:
                self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()

            response = {
                'status': status,
                'message': ""
            }

            # 将响应数据写入输出流
            self.wfile.write(json.dumps(response).encode('utf-8'))

        except ValueError as ve:
            # 返回400错误
            self.send_response(400)  # HTTP 400请求错误
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'status': 'error', 'message': str(ve)}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        except KeyError as ke:
            # 返回400错误
            self.send_response(400)  # HTTP 400请求错误
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'status': 'error', 'message': str(ke)}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        except Exception as ex:
            # 返回500错误
            self.send_response(500)  # HTTP 500服务器错误
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'status': 'error', 'message': 'Internal Server Error: ' + str(ex)}
            self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            # 创建HTML页面的开头部分
            response = """<!DOCTYPE html>
<html>
<head>
    <title>Image Viewer</title>
    <style>
        body {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            padding-top: 60px;
            margin: 0;
        }
        .image-box {
            text-align: center;
            margin: 10px;
            border: 1px solid #ccc;
            padding: 10px;
            display: inline-block;
            max-width: 400px;
        }
        .save {
            position: fixed;
            top: 0;
            right: 60px;
            width: 15%;
            padding: 10px;
            text-align: right;
        }
        .text-input {
            width: 200px;
        }
        .exConfirm {
            display: none; /* 默认隐藏 */
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border: 1px solid black;
            z-index: 1003; /* 确保在最上层 */
        }
        .delConfirm {
            display: none; /* 默认隐藏 */
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: white;
            padding: 20px;
            border: 1px solid black;
            z-index: 1003; /* 确保在最上层 */
        }
        .text-box {
            border: 1px solid gray;
            font-size: 15px;
            position: fixed;
            width: 5%;
            top: 0;
            right: 180px;
            padding: 4px;
            text-align: center;
        }
        img {
            max-width: 100%;
            cursor: pointer;
        }
        p {
            font-size: 0.8em;
        }
        #floating-title {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            padding: 10px;
            background-color: white;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            font-size: 1.5em;
            text-align: center;
            z-index: 1000;
        }
    </style>
    <script>
        function showImageModal(src) {
            const modal = document.createElement('div');
            modal.style.position = 'fixed';
            modal.style.top = '0';
            modal.style.left = '0';
            modal.style.width = '100%';
            modal.style.height = '100%';
            modal.style.backgroundColor = 'rgba(0, 0, 0, 0.8)';
            modal.style.display = 'flex';
            modal.style.justifyContent = 'center';
            modal.style.alignItems = 'center';
            modal.style.zIndex = '1001';
            modal.onclick = () => document.body.removeChild(modal);

            const img = document.createElement('img');
            img.src = src;
            img.style.maxWidth = '90%';
            img.style.maxHeight = '90%';

            modal.appendChild(img);
            document.body.appendChild(modal);
        }

        function saveConfirm() {
            document.getElementById("exConfirm").style.display = "block";
        }

        function deleteConfirm() {
            document.getElementById("delConfirm").style.display = "block";
        }

        function send_action_post(img_list, act, path) {
		    const url = '/';
            const data = {
                "imgs": img_list,
                "action": act,
                "path": path
            };
            fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
            })
            .then(response => response.json())
            .then(data => {
                if (data['status'] == 'success') {
                    alert("操作成功");
                } else {
                    alert("操作失败 ERROR:" + data['message']);
                }
                window.location.reload();
                console.log('Response:', data);
            })
            .catch(error => {
                alert("操作失败 ERROR", error);
                console.error('Error:', error);
            });
        }

        function save() {
            const input_text = document.getElementById("text-input");
            const path = input_text.value;
            console.log('Save path:', path);
            var img_boxs = document.querySelectorAll(".image-box");
			const imgNames = [];
			img_boxs.forEach(box => {
            const labels = box.getElementsByTagName("input");
            const save = labels[0];
            const del = labels[1];
            if (save.checked) {
            const img = box.getElementsByTagName("img")[0];
            if (img) {
    		    const src = img.getAttribute('src');
    		    if (src) { 
        	        imgNames.push(src);
    		    }
            }
            }
		    });
            console.log('Image names:', imgNames);
            send_action_post(imgNames, "save", path);
            document.getElementById("exConfirm").style.display = "none";
        }
        function cancelExp() {
            document.getElementById("exConfirm").style.display = "none";
        }

        function cancelDel() {
            document.getElementById("delConfirm").style.display = "none";
        }

        function deleteImages() {
            var img_boxs = document.querySelectorAll(".image-box");
			const imgNames = [];
			img_boxs.forEach(box => {
            const labels = box.getElementsByTagName("input");
            const save = labels[0];
            const del = labels[1];
            if (del.checked) {
            const img = box.getElementsByTagName("img")[0];
            if (img) {
    		    const src = img.getAttribute('src');
    		    if (src) { 
        	        imgNames.push(src);
    		    }
            }
            }
		    });
            console.log('Image names:', imgNames);
            send_action_post(imgNames, "delete", "none");
            document.getElementById("delConfirm").style.display = "none";
        }
    </script>
</head>
<body>
"""
            image_size = len(os.listdir(PATH))
            localpath = os.path.join(os.getcwd(), "export_full.json")
            response += f"""
    <div id="floating-title">
        Image Viewer
    <div class="save">
        <p class="text-box">files:{image_size}</p>
        <button onclick="saveConfirm()">导出</button> 
        <button onclick="deleteConfirm()">删除</button> 
    </div>
    </div>
    <div id="exConfirm" class="exConfirm">导出路径:
    <input type="text" id="text-input" class="text-input" value="{localpath}"/> 
    <button onclick="save()">导出</button>
    <button onclick="cancelExp()">取消</button>
    </div>
    <div id="delConfirm" class="delConfirm">
    <button onclick="deleteImages()">确认删除</button>
    <button onclick="cancelDel()">取消</button>
    </div>
    <div id="labelImage">
    </div>
"""
            # 在当前目录下查找所有图片文件
            filenames = []
            frame_filenames = []
            for filename in os.listdir(PATH):
                if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp")):
                    filename = os.path.join(PATH, filename)
                    if "frame" in filename:
                        frame_filenames.append(filename)
                    else:
                        filenames.append(filename)
            sorted_filenames = sorted(filenames)
            for filename in sorted_filenames:
                    # 将找到的图片文件添加到HTML页面中
                response += f"""
    <div class="image-box">
        <p>{filename}</p>
        <img src="{filename}" alt="{filename}" onclick="showImageModal('{filename}')">
        保存
        <label><input type="radio" name="{filename}" value="yes" checked="checked" />是</label>
        <label><input type="radio" name="{filename}" value="no" />否</label>
    </div>
"""
            sorted_filenames = sorted(frame_filenames, key=lambda x: int(x[-10:-4]))
            for filename in sorted_filenames:
                    # 将找到的图片文件添加到HTML页面中
                response += f"""
    <div class="image-box">
        <p>{filename}</p>
        <img src="{filename}" alt="{filename}" onclick="showImageModal('{filename}')">
        保存
        <label><input type="radio" name="{filename}" value="yes" checked="checked" />是</label>
        <label><input type="radio" name="{filename}" value="no" />否</label>
    </div>
"""
            # 结束HTML页面
            response += """
</body>
</html>
"""

            # 发送HTML页面作为响应
            self.wfile.write(response.encode("utf-8"))
        else:
            # 对于其他请求（例如请求图片文件），使用默认处理方法
            path = self.translate_path(unquote(self.path))
            if os.path.exists(path):
                super().do_GET()
            else:
                self.send_error(404, "File not found")

def main():
    global PATH
    global PORT
    if len(sys.argv) > 1:
        PATH=sys.argv[1]
    if len(sys.argv) > 2:
        PORT=int(sys.argv[2])
    
    # 设置HTTP服务器
    Handler = ImageRequestHandler
    # 允许重用地址
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving on port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()
            httpd.server_close()

if __name__ == '__main__':
    main()
