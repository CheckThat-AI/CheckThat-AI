export const config = {
  development: {
    apiUrl: 'http://localhost:8000',
    wsUrl: 'ws://localhost:8000',
  },
  production: {
    apiUrl: 'https://claim-normalization.onrender.com',
    wsUrl: 'wss://claim-normalization.onrender.com',
  },
};

export const getApiUrl = () => {
  const env = import.meta.env.MODE || 'development';
  return config[env as keyof typeof config].apiUrl;
};

export const getWsUrl = () => {
  const env = import.meta.env.MODE || 'development';
  return config[env as keyof typeof config].wsUrl;
}; 