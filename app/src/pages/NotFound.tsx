
import { Layout } from '../Layout';

const NotFound = () => {
  return (
    <Layout title="404 - Page Not Found">
      <div className="container mx-auto mt-32 py-16 px-4 sm:px-6 lg:px-8 text-center">
        <h1 className="text-4xl font-bold text-foreground mb-4">404 - Page Not Found</h1>
        <p className="text-lg text-muted-foreground">The page you are looking for does not exist.</p>
        <a href="/" className="text-primary hover:underline mt-4 block">Go to Home Page</a>
      </div>
    </Layout>
  );
};

export default NotFound; 