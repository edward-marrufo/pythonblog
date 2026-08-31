// Import React hooks
import { useState } from "react";
import {
  Container,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Box
} from "@mui/material";

const API_BASE = "/api/v1/auth"

// Login page component
function RegisterPage() {

  // State for new login email
  const [email, setEmail] = useState("")

  // State for new login username
  const [username, setUsername] = useState("");

  // State for new login password
  const [password, setPassword] = useState("");

  // Function to submit a new login request
  const registerRequest = async () => {

    // Send POST request to FastAPI
    const response = await fetch(`${API_BASE}/register`, {

      method: "POST",

      headers: {
        "Content-Type": "application/json"
      },

      body: JSON.stringify({
        email: email,
        username: username,
        password: password
      })

    });

    // Convert response JSON
    const newRegister = await response.json();
    //console.log(newRegister)

    // Clear input fields
    setEmail("");
    setUsername("");
    setPassword("");
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
                  Register a New Account
                </Typography>

                <TextField
                  fullWidth
                  label="Email"
                  margin="normal"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />
    
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
                  onClick={registerRequest}
                >
                  Register
                </Button>
              </CardContent>
            </Card>
          </Box>
        </Container>
  );
}

export default RegisterPage;