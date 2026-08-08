#!/usr/bin/env node

/**
 * Password Hash Generator for Admin Login
 * 
 * Usage:
 *   node scripts/generate-password-hash.js <password>
 * 
 * Example:
 *   node scripts/generate-password-hash.js mySecretPassword123
 * 
 * Then add the output to your .env file as REACT_APP_ADMIN_PASSWORD_HASH
 */

const crypto = require("crypto");

const password = process.argv[2];

if (!password) {
  console.error("Usage: node generate-password-hash.js <password>");
  console.error("Example: node generate-password-hash.js mySecretPassword123");
  process.exit(1);
}

const hash = crypto.createHash("sha256").update(password).digest("hex");

console.log("\n=== Password Hash Generated ===\n");
console.log("Add these lines to your .env file:\n");
console.log(`REACT_APP_ADMIN_USERNAME=admin`);
console.log(`REACT_APP_ADMIN_PASSWORD_HASH=${hash}`);
console.log("\n(Change 'admin' to your preferred username)\n");

