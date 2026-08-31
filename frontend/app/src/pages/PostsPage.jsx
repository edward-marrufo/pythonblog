import { useEffect, useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Container,
  Card,
  CardContent,
  TextField,
  Button,
  Box
} from "@mui/material";

const API_BASE = "/api/v1"

function PostsPage({ user, setUser }) {
  const [posts, setPosts] = useState([]);
  const [title, setTitle] = useState("");
  const [text, setText] = useState("");

  useEffect(() => {
    fetch(`${API_BASE}/posts`, { credentials: "include" })
      .then((res) => res.json())
      .then(setPosts);
  }, []);

  const createPost = async () => {
    const res = await fetch(`${API_BASE}/posts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ title, text }),
    });

    const newPost = await res.json();
    setPosts((prev) => [newPost, ...prev]);
    setTitle("");
    setText("");
  };

  const deletePost = async (id) => {
    await fetch(`${API_BASE}/posts/${id}`, {
      method: "DELETE",
      credentials: "include",
    });
    setPosts((prev) => prev.filter((p) => p.id !== id));
  };

  const handleLogout = async () => {
    await fetch(`${API_BASE}/auth/logout`, {
      method: "POST",
      credentials: "include",
    });
    setUser(null);
  };

  return (
    <>
      {/* 🔝 NAVBAR */}
      <AppBar position="static">
        <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
          <Typography variant="h6">My Blog</Typography>
          <Box>
            {user?.username}{" "}
            <Button color="inherit" onClick={handleLogout}>
              Logout
            </Button>
          </Box>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ mt: 4 }}>
        {/* ✍️ CREATE POST */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6">Create Post</Typography>

            <TextField
              fullWidth
              label="Title"
              margin="normal"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />

            <TextField
              fullWidth
              multiline
              rows={4}
              label="Content"
              margin="normal"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />

            <Button variant="contained" onClick={createPost}>
              Post
            </Button>
          </CardContent>
        </Card>

        {/* 📰 POSTS LIST */}
        {posts.map((post) => (
          <Card key={post.id} sx={{ mb: 2 }}>
            <CardContent>
              <Typography variant="h6">{post.title}</Typography>
              <Typography variant="body2" color="text.secondary">
                by {post.author.username}
              </Typography>

              <Typography sx={{ mt: 2 }}>{post.text}</Typography>

              {post.can_delete && (
                <Button
                  sx={{ mt: 2 }}
                  color="error"
                  onClick={() => deletePost(post.id)}
                >
                  Delete
                </Button>
              )}
            </CardContent>
          </Card>
        ))}
      </Container>
    </>
  );
}

export default PostsPage;