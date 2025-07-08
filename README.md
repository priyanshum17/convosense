# ConvoSense

ConvoSense is a real-time messaging application built with Flask and Flask-SocketIO. It provides user authentication, one-on-one messaging, and real-time user status updates.

## Features

*   User Registration and Login
*   Secure Password Hashing
*   Real-time One-on-One Messaging
*   Real-time User Online/Offline Status
*   Retrieve Message History between users
*   List Active Users

## Setup

### Prerequisites

*   Python 3.x
*   pip (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/convosense.git
    cd convosense
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Initialization:**
    The application uses SQLite for its database. The database file (`site.db`) will be created automatically when you run the application for the first time.

## Running the Application

To start the Flask development server and WebSocket server:

```bash
python main.py
```

The application will be accessible at `http://127.0.0.1:5005/`.

## API Endpoints (HTTP)

All HTTP endpoints are under the `/auth` blueprint.

### 1. Register a New User

*   **URL:** `/auth/register`
*   **Method:** `POST`
*   **Request Body (JSON):**
    ```json
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```
*   **Success Response:**
    ```json
    {
        "message": "User registered successfully"
    }
    ```
    (Status: 201 Created)
*   **Error Responses:**
    *   `{"message": "Username and password are required"}` (Status: 400 Bad Request)
    *   `{"message": "User already exists"}` (Status: 409 Conflict)

### 2. User Login

*   **URL:** `/auth/login`
*   **Method:** `POST`
*   **Request Body (JSON):**
    ```json
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```
*   **Success Response:**
    ```json
    {
        "message": "Logged in successfully",
        "user_id": 123
    }
    ```
    (Status: 200 OK)
*   **Error Response:**
    *   `{"message": "Invalid credentials"}` (Status: 401 Unauthorized)

### 3. Delete a User

*   **URL:** `/auth/delete_user`
*   **Method:** `DELETE`
*   **Request Body (JSON):**
    ```json
    {
        "username": "your_username",
        "password": "your_password"
    }
    ```
*   **Success Response:**
    ```json
    {
        "message": "User deleted successfully"
    }
    ```
    (Status: 200 OK)
*   **Error Response:**
    *   `{"message": "Invalid credentials"}` (Status: 401 Unauthorized)

## WebSocket Events

The WebSocket server is integrated with Flask-SocketIO. The client-side `static/index.html` provides an example of how to connect and interact.

### 1. `connect`

*   **Description:** Triggered when a client successfully connects to the WebSocket.
*   **Client-side connection:**
    ```javascript
    // Example: Connect with a user_id query parameter
    const socket = io('http://127.0.0.1:5000', {
        query: { user_id: YOUR_USER_ID }
    });
    ```
*   **Server Emits:** `user_status` (broadcast to all clients) when a user connects and their `is_active` status is updated.

### 2. `disconnect`

*   **Description:** Triggered when a client disconnects from the WebSocket.
*   **Server Emits:** `user_status` (broadcast to all clients) when a user disconnects and their `is_active` status is updated.

### 3. `message`

*   **Description:** Sends a real-time message from one user to another.
*   **Client Emits:**
    ```javascript
    socket.emit('message', {
        sender_id: YOUR_SENDER_ID,
        receiver_id: TARGET_RECEIVER_ID,
        content: "Hello, how are you?"
    });
    ```
*   **Server Emits:**
    *   `new_message` to the `receiver_id`'s connected client.
    *   `message_sent` back to the `sender_id`'s client for confirmation.

### 4. `get_active_users`

*   **Description:** Requests a list of currently active (online) users.
*   **Client Emits:**
    ```javascript
    socket.emit('get_active_users');
    ```
*   **Server Emits:** `active_users_list` to the requesting client.
    ```json
    [
        {"id": 1, "username": "user1"},
        {"id": 2, "username": "user2"}
    ]
    ```

### 5. `get_user_status`

*   **Description:** Requests the online/offline status of a specific user.
*   **Client Emits:**
    ```javascript
    socket.emit('get_user_status', { user_id: TARGET_USER_ID });
    ```
*   **Server Emits:** `user_status` to the requesting client.
    ```json
    {
        "user_id": TARGET_USER_ID,
        "is_active": true
    }
    ```

### 6. `get_user_messages`

*   **Description:** Requests the message history between two specific users.
*   **Client Emits:**
    ```javascript
    socket.emit('get_user_messages', {
        user_id: YOUR_USER_ID,
        other_user_id: OTHER_USER_ID
    });
    ```
*   **Server Emits:** `user_messages` to the requesting client.
    ```json
    {
        "messages": [
            {
                "sender_id": 1,
                "receiver_id": 2,
                "content": "Hi there!",
                "timestamp": "2023-10-27T10:00:00.000Z"
            },
            // ... more messages
        ]
    }
    ```

## Technologies Used

*   **Flask:** Web framework
*   **Flask-SocketIO:** WebSocket integration
*   **Flask-SQLAlchemy:** ORM for database interactions
*   **Eventlet:** Asynchronous I/O library for SocketIO
*   **Werkzeug:** For password hashing
