from server_kimia_fisik import create_app
from server_kimia_fisik.pyrebase_init import initialize_firebase

app = create_app()
firebase = initialize_firebase()
