# 📘 Content Management System API

This is a RESTful API for a Content Management System (CMS), built to manage articles and their associated comments, with user registration and authentication.

## Features

- User authentication and authorization
- Intuitive content editor
- Media management (images, articles, etc.)
- Role-based access control
- SEO-friendly content structure
- API support for integrations

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Igboke/content-management-system.git
    ```
2. Navigate to the project directory:
    ```bash
    cd content-management-system
    ```
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Set up environment variables in a `.env` file:
    ```plaintext
    SECRET_KEY=your-secret-key
    ```
5. Run the application:
    navigate to directory housing manage.py file
    ```bash
    python manage.py runserver
    ```

## 📚 Endpoints

### 📝 Articles

- **List Articles**  
  `GET /articles/`  
  Returns all published articles.  
  🔒 Requires Authentication  

- **Create Article**  
  `POST /articles/`  
  Create a new article.  
  🔒 Requires Authentication  

- **Retrieve Article**  
  `GET /articles/{slug}/`  
  Get details of a specific article.  
  🔒 Requires Authentication  

- **Update Article**  
  `PUT /articles/{slug}/`  
  Update all fields of a specific article.  
  🔒 Requires Authentication  

- **Partial Update Article**  
  `PATCH /articles/{slug}/`  
  Update some fields of an article.  
  🔒 Requires Authentication  

- **Delete Article**  
  `DELETE /articles/{slug}/`  
  Delete a specific article.  
  🔒 Requires Authentication  

- **Search Articles by Title**  
  `GET /articles/search/`  
  🔒 Requires Authentication  

- **Search Articles by Author's Name**  
  `GET /articles/search/{name}/`  
  🔒 Requires Authentication  

---

### 💬 Comments

- **List Comments for an Article**  
  `GET /articles/{slug}/comments/`  
  🔒 Requires Authentication  

- **Create Comment on an Article**  
  `POST /articles/{slug}/comments/`  
  🔒 Requires Authentication  

- **Retrieve Specific Comment**  
  `GET /articles/{slug}/comments/{id}/`  
  🔒 Requires Authentication  

- **Update Comment**  
  `PUT /articles/{slug}/comments/{id}/`  
  🔒 Requires Authentication  

- **Partial Update Comment**  
  `PATCH /articles/{slug}/comments/{id}/`  
  🔒 Requires Authentication  

- **Delete Comment**  
  `DELETE /articles/{slug}/comments/{id}/`  
  🔒 Requires Authentication  

---

### 🔐 Auth & Users

- **Token Authentication**  
  `POST /auth/token/`  
  Request:
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```  
  🔒 Requires Authentication  

- **User Registration**  
  `POST /user/create/`

---

## 🧱 Schema: Article (`ArticlesSerializers`)

```json
{
  "id": "integer",
  "title": "string",
  "slug": "string (read-only)",
  "author": {
    "id": "integer",
    "username": "string",
    "email": "email",
    "first_name": "string",
    "last_name": "string",
    "other_name": "string or null",
    "occupation": "string or null",
    "bio": "string or null",
    "profile_picture": "uri or null"
  },
  "content": "string",
  "created_at": "datetime",
  "updated_at": "datetime",
  "picture": "uri (optional)",
  "is_published": "draft | published | archived | review",
  "comment": [/* list of comment objects */]
}
```

---

## 💬 Schema: Comment (`CommentSerializers`)

```json
{
  "id": "integer",
  "author": {
    "id": "integer",
    "username": "string",
    "email": "email"
  },
  "content": "string",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

---

## 👤 Schema: User (`CustomUser`)

```json
{
  "id": "integer",
  "username": "string",
  "email": "string",
  "first_name": "string",
  "last_name": "string",
  "other_name": "string or null",
  "occupation": "string or null",
  "bio": "string or null",
  "profile_picture": "uri or null"
}
```


## 🧪 Swagger UI

Append `api/schema/redoc` or `/api/schema/swagger-ui/` to your base URL to view interactive API documentation via Swagger UI.


## Technologies Used

- **Backend**: django
- **Database**: SQLite3
- **Authentication**: restframework authentication token

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch:
    ```bash
    git checkout -b new-feature
    ```
3. Commit your changes:
    ```bash
    git commit -m "Add new feature"
    ```
4. Push to your branch:
    ```bash
    git push origin new-feature
    ```
5. Open a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For questions or feedback, please contact:
- **Email**: danieligboke669@example.com
- **GitHub**: [Igboke](https://github.com/Igboke)
- **Website**: TO BE UPDATED