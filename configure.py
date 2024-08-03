def configure_upload_folder():
    from flask import current_app
    import os

    base_dir = os.path.abspath(os.path.dirname(__file__))

    upload_folder = os.path.join(base_dir, 'files')

    current_app.config['UPLOAD_FOLDER'] = upload_folder

