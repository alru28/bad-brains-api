const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const router = express.Router();

const secret = process.env.JWT_SECRET || 'example_secret';

// Test endpoint
router.get('/test', (req, res) => {
    console.log("Test endpoint hit");
    res.json({ message: 'Auth route is working!' });
});

// Register user
router.post('/register', async (req, res) => {
    console.log('Register endpoint hit with body:', req.body);
    const { username, email, password } = req.body;
    
    if (!username || !email || !password) {
        return res.status(400).json({ error: 'All fields are required' });
    }

    try {
        const existingUser = await req.pool.query(
            'SELECT * FROM users WHERE username = $1 OR email = $2',
            [username, email]
        );

        if (existingUser.rows.length > 0) {
            return res.status(400).json({ error: 'User already exists' });
        }

        const hashedPassword = await bcrypt.hash(password, 10);
        await req.pool.query(
            'INSERT INTO users (username, email, password) VALUES ($1, $2, $3)',
            [username, email, hashedPassword]
        );

        res.status(201).json({ message: 'User registered successfully' });
    } catch (error) {
        console.error('Register error:', error);
        res.status(500).json({ error: 'Server error during registration' });
    }
});

// Login user
router.post('/login', async (req, res) => {
    console.log('Login endpoint hit with body:', req.body);
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ error: 'Username and password are required' });
    }

    try {
        const userResult = await req.pool.query(
            'SELECT * FROM users WHERE username = $1',
            [username]
        );
        
        const user = userResult.rows[0];
        
        if (user && await bcrypt.compare(password, user.password)) {
            const token = jwt.sign(
                { username: user.username, email: user.email },
                secret,
                { expiresIn: '24h' }
            );
            res.json({ token: "Bearer " + token });
        } else {
            res.status(400).json({ error: 'Invalid credentials' });
        }
    } catch (error) {
        console.error('Login error:', error);
        res.status(500).json({ error: 'Server error during login' });
    }
});

// Verify
router.get('/verify', (req, res) => {
    const authHeader = req.headers['authorization'];

    if (!authHeader || !authHeader.startsWith("Bearer ")) {
        return res.status(401).json({ error: 'Authorization JWT token is missing or malformed' });
    }
    
    // Remove "Bearer " prefix
    const token = authHeader.split(" ")[1];

    // Verify
    jwt.verify(token, secret, (err, decoded) => {
        if (err) {
            return res.status(401).json({ error: 'Invalid token' });
        }

        res.status(200).json({ message: 'Token is valid', user: decoded });
    });
});

module.exports = router;