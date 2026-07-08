import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import DashboardPage from "./pages/DashboardPage";
import IndustryPage from "./pages/IndustryPage";
import StocksPage from "./pages/StocksPage";
import XIntelPage from "./pages/XIntelPage";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/x-intel" replace />} />
        <Route path="/x-intel" element={<XIntelPage />} />
        <Route path="/industry" element={<IndustryPage />} />
        <Route path="/stocks" element={<StocksPage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
      </Routes>
    </Layout>
  );
}

