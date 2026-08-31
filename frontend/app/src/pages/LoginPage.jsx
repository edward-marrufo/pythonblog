import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Link as RouterLink} from "react-router-dom";

import {
  Container,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box,
  Link
} from "@mui/material";

const API_BASE = "/api/v1/auth"

function LoginPage({ setUser }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const loginRequest = async () => {
    try {
      const response = await fetch(`${API_BASE}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
        credentials: "include",
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Login failed");
      }

      const data = await response.json();
      setUser(data);
      navigate("/posts");
    } catch (err) {
      console.error("Login error:", err);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center"
        }}
      >
        <Card sx={{ width: "100%", p: 2 }}>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Login
            </Typography>

            <TextField
              fullWidth
              label="Username"
              margin="normal"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
            />

            <TextField
              fullWidth
              label="Password"
              type="password"
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />

            <Button
              fullWidth
              variant="contained"
              sx={{ mt: 2 }}
              onClick={loginRequest}
            >
              Login
            </Button>
            <Typography sx={{ mt: 2 }}>
              Don’t have an account?{" "}
              <Link component={RouterLink} to={`/register`}>
              Register here
              </Link>
              </Typography>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
}

export default LoginPage;