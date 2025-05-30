import { Navigate, useLocation } from 'react-router';
import { useAuth } from './AuthContext';

const RequireAuth = ({ children }) => {
    const { isAuthenticated , loading } = useAuth()
    const location = useLocation();
    if(loading) return <div>Loading...</div>
    if (!isAuthenticated) {
        return <Navigate to="/" state={{ from: location }} replace />;
    }
    return children;
};

export default RequireAuth;
