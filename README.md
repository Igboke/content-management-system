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

## Authentication

- **Token Authentication**: Use `Authorization` header with prefix "Token".  
  Example: `Authorization: Token <your_token>`
- **Cookie Authentication**: Use `sessionid` cookie.


## 📚 Endpoints

#### List/Create Articles
- **GET** `/api/v1/articles/`  
  **Description**: List published articles.  
  **Security**: Token or Cookie  
  **Response**: `200 OK` - Array of [`ArticlesSerializers`](#articlesserializers)

- **POST** `/api/v1/articles/`  
  **Description**: Create a new article.  
  **Security**: Token or Cookie  
  **Request Body**: [`ArticlesSerializers`](#articlesserializers) (JSON/form-data/x-www-form-urlencoded)  
  **Response**: `201 Created` - [`ArticlesSerializers`](#articlesserializers)

#### Retrieve/Update/Delete Article
- **GET** `/api/v1/articles/{slug}/`  
  **Description**: Retrieve a specific article by slug.  
  **Security**: Token or Cookie  
  **Parameters**:  
    - `slug` (string, path)  
  **Response**: `200 OK` - [`ArticlesSerializers`](#articlesserializers)

- **PUT** `/api/v1/articles/{slug}/`  
  **Description**: Fully update an article.  
  **Security**: Token or Cookie  
  **Parameters**:  
    - `slug` (string, path)  
  **Request Body**: [`ArticlesSerializers`](#articlesserializers)  
  **Response**: `200 OK` - Updated article.

- **PATCH** `/api/v1/articles/{slug}/`  
  **Description**: Partially update an article.  
  **Security**: Token or Cookie  
  **Parameters**:  
    - `slug` (string, path)  
  **Request Body**: [`PatchedArticlesSerializers`](#patchedarticlesserializers)  
  **Response**: `200 OK` - Updated article.

- **DELETE** `/api/v1/articles/{slug}/`  
  **Description**: Delete an article.  
  **Security**: Token or Cookie  
  **Parameters**:  
    - `slug` (string, path)  
  **Response**: `204 No Content`

---

### Comments

#### List/Create Comments for an Article
- **GET** `/api/v1/articles/{slug}/comments/`  
  **Description**: List comments for an article.  
  **Security**: Token, Cookie, or Public  
  **Parameters**:  
    - `slug` (string, path)  
  **Response**: `200 OK` - Array of [`CommentSerializers`](#commentserializers)

- **POST** `/api/v1/articles/{slug}/comments/`  
  **Description**: Create a new comment.  
  **Security**: Token or Cookie  
  **Parameters**:  
    - `slug` (string, path)  
  **Request Body**: [`CommentSerializers`](#commentserializers)  
  **Response**: `201 Created` - Created comment.

#### Manage Specific Comment
- **GET** `/api/v1/articles/{slug}/comments/{id}/`  
  **Description**: Retrieve a comment.  
  **Security**: Token, Cookie, or Public  
  **Parameters**:  
    - `slug` (string, path)  
    - `id` (integer, path)  
  **Response**: `200 OK` - [`CommentSerializers`](#commentserializers)

- **PUT/PATCH/DELETE** `/api/v1/articles/{slug}/comments/{id}/`  
  **Description**: Update/delete a comment (author only).  
  **Security**: Token or Cookie  
  **Parameters**:  
    - `slug` (string, path)  
    - `id` (integer, path)  
  **Request Body** (PUT/PATCH): [`CommentSerializers`](#commentserializers) or [`PatchedCommentSerializers`](#patchedcommentserializers)  
  **Response**:  
    - `200 OK` (PUT/PATCH)  
    - `204 No Content` (DELETE)

---

### Search

- **GET** `/api/v1/articles/search/`  
  **Description**: Search articles by title.  
  **Security**: Token, Cookie, or Public  
  **Response**: `200 OK` - Array of [`ArticlesSerializers`](#articlesserializers)

- **GET** `/api/v1/articles/search/{email}/`  
  **Description**: Search articles by author's email.  
  **Security**: Token, Cookie, or Public  
  **Parameters**:  
    - `email` (string, path)  
  **Response**: `200 OK` - Array of [`ArticlesSearch`](#articlessearch)

---

### Authentication

- **POST** `/api/v1/auth/login/`  
  **Description**: User login.  
  **Request Body**: [`Login`](#login)  
  **Response**: `200 OK` - Login details.

- **POST** `/api/v1/auth/token/`  
  **Description**: Obtain auth token.  
  **Request Body**: [`AuthToken`](#authtoken)  
  **Response**: `200 OK` - Token details.

- **GET** `/api/v1/auth/verify/{user_id}/{token}/`  
  **Description**: Email verification.  
  **Parameters**:  
    - `user_id` (integer, path)  
    - `token` (string, path)  
  **Response**: `200 OK` - [`EmailVerificationResponse`](#emailverificationresponse)

---

### User Registration

- **POST** `/api/v1/user/create/`  
  **Description**: Register a new user.  
  **Request Body**: [`UserRegistration`](#userregistration)  
  **Response**: `201 Created` - User details.

---

## Schemas

### ArticlesSerializers
| Property        | Type                | Description                              | Required |
|-----------------|---------------------|------------------------------------------|----------|
| `id`            | integer (read-only) | Article ID                               | Yes      |
| `title`         | string              | Article title (max 200 chars)            | Yes      |
| `slug`          | string (read-only)  | URL-friendly slug                        | Yes      |
| `author`        | [CustomUser](#customuser) | Author details                    | Yes      |
| `content`       | string              | Article content                          | Yes      |
| `created_at`    | datetime (read-only)| Creation timestamp                       | Yes      |
| `updated_at`    | datetime (read-only)| Last update timestamp                    | Yes      |
| `picture`       | string (URI)        | Optional article image                   | No       |
| `is_published`  | enum (`draft`, `published`, `archived`, `review`) | Publication status | Yes |
| `comment`       | Array of [CommentSerializers](#commentserializers) | Comments | Yes |

### CommentSerializers
| Property        | Type                | Description                              | Required |
|-----------------|---------------------|------------------------------------------|----------|
| `id`            | integer (read-only) | Comment ID                               | Yes      |
| `author`        | [CustomUser](#customuser) | Author details                    | Yes      |
| `content`       | string              | Comment content                          | Yes      |
| `created_at`    | datetime (read-only)| Creation timestamp                       | Yes      |
| `updated_at`    | datetime (read-only)| Last update timestamp                    | Yes      |

### CustomUser
| Property            | Type                | Description                              | Required |
|---------------------|---------------------|------------------------------------------|----------|
| `id`                | integer (read-only) | User ID                                  | Yes      |
| `username`          | string              | Username (max 150 chars)                 | Yes      |
| `email`             | string (email)      | Valid email address                      | Yes      |
| `first_name`        | string              | First name (max 150 chars)               | No       |
| `last_name`         | string              | Last name (max 150 chars)                | No       |
| `other_name`        | string              | Optional other name                      | No       |
| `occupation`        | string              | Occupation (max 100 chars)               | No       |
| `bio`               | string              | Biography                                | No       |
| `profile_picture`   | string (URI)        | Profile image URL                        | No       |

### AuthToken
| Property   | Type     | Description          | Required |
|------------|----------|----------------------|----------|
| `username` | string   | Username             | Yes      |
| `password` | string   | Password             | Yes      |
| `token`    | string   | Auth token (read-only)| Yes     |

### UserRegistration
| Property            | Type     | Description                              | Required |
|---------------------|----------|------------------------------------------|----------|
| `username`          | string   | Username (max 150 chars)                 | Yes      |
| `email`             | string   | Valid email address                      | Yes      |
| `password`          | string   | Password (write-only)                    | Yes      |
| `password2`         | string   | Confirm password (write-only)            | Yes      |
| `first_name`        | string   | First name (max 150 chars)               | No       |
| `last_name`         | string   | Last name (max 150 chars)                | No       |
| `other_name`        | string   | Optional other name                      | No       |
| `occupation`        | string   | Occupation (max 100 chars)               | No       |
| `bio`               | string   | Biography                                | No       |
| `profile_picture`   | string   | Profile image URL                        | No       |

### Other Schemas
- **PatchedArticlesSerializers**: Partial update version of `ArticlesSerializers`.
- **PatchedCommentSerializers**: Partial update version of `CommentSerializers`.
- **ArticlesSearch**: Includes `title`, `slug`, `author`, `content`, `created_at`.
- **Login**: Requires `email` and `password`.
- **EmailVerificationResponse**: Contains `detail` (string).

## Test
To run all tests
```bash
  python manage.py test
  ```

To run a specific class of test
```bash
  python manage.py test myapp.testsfile.TestClass
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
- **Email**: danieligboke669@gmail.com
- **GitHub**: [Igboke](https://github.com/Igboke)
- **Project Website**: https://content-management-system-rjdu.onrender.com/api/schema/swagger-ui/
