## [Accessing the Google Drive APIs](https://nathanielng.github.io/python-snippets/remote/GOOGLE_APIs)

### 1. Create a new project

1. Go to [console.developers.google.com](http://console.developers.google.com/project)
2. Click "+Create Project". Key in a project name and click "Create"

### 2. Create a Service Account and download the API key

1. Go to the Navigation menu, choose "APIs & Services > Credentials"
2. Click "+Create Credentials" and choose the "Service Account" option.
3. Enter a service account name & ID and click "Create"
4. When prompted for the optional service account permissions, click "Continue"
5. Click "+Create Key".
6. Choose "JSON" for the key type.
7. Click "Create" (the private key will be saved to your computer)

### 3. Enabling APIs & Services

1. Go to the Navigation menu, choose "APIs & Services > Dashboard"
2. Select the "+Enable APIs and Services"
3. Search for the "Google Drive API" and click "Enable"
4. Go back, then search for the "Google Sheets API" and click "Enable"

