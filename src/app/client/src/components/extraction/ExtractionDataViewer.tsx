import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Download, Eye, EyeOff } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

// Custom scrollbar styles
const scrollbarStyles = `
  .custom-scrollbar::-webkit-scrollbar {
    height: 8px;
    width: 8px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: rgba(148, 163, 184, 0.3);
    border-radius: 4px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb:hover {
    background: rgba(20, 190, 1, 0.5);
  }
  .custom-scrollbar {
    scrollbar-width: thin;
    scrollbar-color: gray transparent;
  }
`;

interface ExtractionDataViewerProps {
  fileData: {
    file_path: string;
    file_name: string;
    data: any[];
    columns: string[];
  } | null;
}

export default function ExtractionDataViewer({ fileData }: ExtractionDataViewerProps) {
  const [isExpanded, setIsExpanded] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;
  const { toast } = useToast();

  if (!fileData) {
    return null;
  }

  const { file_name, data, columns } = fileData;
  const totalPages = Math.ceil(data.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentData = data.slice(startIndex, endIndex);

  const handleDownload = () => {
    try {
      // Convert data to CSV format
      const csvContent = [
        columns.join(','),
        ...data.map(row => columns.map(col => `"${(row[col] || '').toString().replace(/"/g, '""')}"`).join(','))
      ].join('\n');

      // Create and download file
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', file_name);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      toast({
        title: "Download Complete",
        description: `${file_name} has been downloaded successfully.`,
        variant: "default",
      });
    } catch (error) {
      toast({
        title: "Download Failed", 
        description: "Failed to download the file. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <>
      <style>{scrollbarStyles}</style>
      <Card className="mt-6 bg-gradient-to-l from-zinc-950 to-zinc-950 via-cardbg-900 border border-slate-800 shadow-2xl">
        <CardHeader>
        <div className="flex items-center justify-between"
        >
          <CardTitle className="text-white text-lg font-semibold">
            Extracted Data ({data.length} rows)
          </CardTitle>
          <div className="flex gap-2 text-white">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsExpanded(!isExpanded)}
              className="flex items-center gap-2 
              bg-gradient-to-l from-zinc-950 to-zinc-950 via-cardbg-900 border border-slate-800 shadow-2xl"
            >
              {isExpanded ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              {isExpanded ? 'Hide Data' : 'Show Data'}
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleDownload}
              className="flex items-center gap-2
              bg-gradient-to-l from-zinc-950 to-zinc-950 via-cardbg-900 border border-slate-800 shadow-2xl"
            >
              <Download className="h-4 w-4" />
              Download CSV
            </Button>
          </div>
        </div>
      </CardHeader>
      
      {isExpanded && (
        <CardContent>
          <div className="border-solid rounded-md overflow-hidden border-slate-800 shadow-2xl">
            <div className="overflow-x-auto custom-scrollbar">
              <table className="w-full border-collapse text-white">
                <thead>
                  <tr className="bg-transparent">
                    {columns.map((column, index) => (
                      <th key={index} className="border border-cyan-800 shadow-2xl px-4 py-2 text-left font-medium">
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {currentData.map((row, rowIndex) => (
                    <tr key={startIndex + rowIndex} className="hover:bg-transparent hover:text-cyan-400">
                      {columns.map((column, colIndex) => (
                        <td key={colIndex} className="border border-cyan-800 shadow-2xl px-4 py-2 text-sm">
                          <div className="max-w-xs truncate" title={row[column]}>
                            {row[column] || ''}
                          </div>
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {totalPages > 1 && (
              <div className="flex items-center justify-between px-4 py-3 border-t border-slate-800 shadow-2xl">
                <div className="text-sm text-white">
                  Showing {startIndex + 1} to {Math.min(endIndex, data.length)} of {data.length} entries
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                  >
                    Previous
                  </Button>
                  <span className="px-3 py-1 text-sm">
                    Page {currentPage} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      )}
    </Card>
    </>
  );
} 