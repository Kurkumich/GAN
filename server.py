from flask import Flask, request, send_file, jsonify
from pyngrok import ngrok
from flask_cors import CORS
import io
import random
import numpy as np
from PIL import Image
import cv2

app = Flask(__name__)
CORS(app)

ATTRS = ['age', 'gender', 'smile']

@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        data = request.json
        print("Полученные данные:", data)


        required_params = ['age', 'gender', 'smile']
        for param in required_params:
            if param not in data:
                return jsonify({"error": f"Missing parameter: {param}"}), 400


        num_samples = 1
        noise_seed = random.randint(0, 10000)

        latent_codes = sample_codes(generator, num_samples, latent_space_type, noise_seed)

        if generator.gan_type == 'stylegan' and latent_space_type == 'W':
            synthesis_kwargs = {'latent_space_type': 'W'}
        else:
            synthesis_kwargs = {}


        new_codes = latent_codes.copy()
        for attr_name in ATTRS:
            if attr_name in data:
                new_codes += boundaries[attr_name] * float(dataa[attr_name])

        new_images = generator.easy_synthesize(new_codes, **synthesis_kwargs)['image']


        image_array = new_images[0] 


        if len(image_array.shape) == 3 and image_array.shape[2] == 3: 
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)


        if image_array.dtype == np.float32 or image_array.dtype == np.float64:
            image_array = (np.clip(image_array, 0, 1) * 255).astype(np.uint8)


        success, encoded_image = cv2.imencode('.jpg', image_array,
                                           [int(cv2.IMWRITE_JPEG_QUALITY), 95])

        if not success:
            return jsonify({"error": "Image encoding failed"}), 500


        img_io = io.BytesIO(encoded_image.tobytes())
        img_io.seek(0)

        return send_file(img_io, mimetype='image/jpeg')


    except Exception as e:
        print("Ошибка:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    ngrok.set_auth_token("2xgzIxIsvkh6NsRpZ8DqIflvpzd_6QfdoLeT4SZa5e8XWXMza")
    public_url = ngrok.connect(5000).public_url
    print(f" * Сервер доступен по адресу: {public_url}/generate")
    app.run(port=5000)
