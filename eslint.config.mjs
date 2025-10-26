import react from "eslint-plugin-react";

export default [
  {
    ignores: [
      "node_modules/**",
      ".next/**",
      ".vercel/**",
      "venv/**",
      "dist/**",
      "build/**",
      ".env*",
    ],
  },
  {
    files: ["**/*.{js,jsx,ts,tsx}"],
    plugins: {
      react,
    },
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
    },
    rules: {
      "react/no-unescaped-entities": "error",
      "@typescript-eslint/no-unused-vars": "warn",
    },
  },
];