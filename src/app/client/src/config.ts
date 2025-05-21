export const config = {
  development: {
    apiUrl: 'http://localhost:8000',
  },
  production: {
    apiUrl: 'https://api.your-production-domain.com', // Replace with your actual production API URL
  },
};

export const getApiUrl = () => {
  const env = import.meta.env.MODE || 'development';
  return config[env as keyof typeof config].apiUrl;
}; 