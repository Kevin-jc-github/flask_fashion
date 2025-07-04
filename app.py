from flask import Flask, render_template, request
from utils.search_utils import search_by_text, search_by_image
from utils.gcs_utils import download
import os
import shutil

app = Flask(__name__)

def clear_image_cache():
    """清空旧图片缓存目录"""
    cache_dir = os.path.join("flask", "static", "images_cache")
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    os.makedirs(cache_dir)

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        query = request.form.get('text_query', '').strip()
        image = request.files.get('image_query')
        page = int(request.args.get("page", 1))  # 当前页
        per_page = 12  # ✅ 每页显示图片数改为 12

        clear_image_cache()
        image_paths = []

        if query:
            all_filenames = search_by_text(query)
        elif image and image.filename != '':
            temp_path = os.path.join("flask", "static", "images_cache", "uploaded.jpg")
            image.save(temp_path)
            all_filenames = search_by_image(temp_path)
        else:
            all_filenames = []

        # 进行分页切片
        start = (page - 1) * per_page
        end = start + per_page
        current_page_files = all_filenames[start:end]
        total_pages = (len(all_filenames) + per_page - 1) // per_page

        for fname in current_page_files:
            gcs_path = fname  # ✅ 直接使用 GCS 的相对路径
            local_path = download("clip-flickr-images-jcz", gcs_path)
            rel_path = os.path.relpath(local_path, 'flask/static')
            image_paths.append(rel_path)

        return render_template(
            'results.html',
            images=image_paths,
            query=query or image.filename,
            page=page,
            total_pages=total_pages,
            total_results=len(all_filenames)  # ✅ 总数量用于前端展示
        )

    # ✅ GET 请求直接回首页
    return render_template('index.html')




if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))  # Render 会提供 $PORT 环境变量
    app.run(debug=False, host='0.0.0.0', port=port)
