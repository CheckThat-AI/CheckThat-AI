import React, { useState } from 'react';
import { BarChart3, CheckCircle, XCircle, Cloud, Database, Clock, Target, ChevronDown, ChevronUp, Download } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';

interface EvaluationResultsSectionProps {
  evaluationResult: any;
  isVisible: boolean;
}

export default function EvaluationResultsSection({ 
  evaluationResult, 
  isVisible 
}: EvaluationResultsSectionProps) {
  const [isTestCasesOpen, setIsTestCasesOpen] = useState(false);

  if (!isVisible || !evaluationResult) {
    return null;
  }

  // Add error boundary-like behavior for safety
  try {
    // Validate and normalize the evaluation result data
    const safeEvaluationResult = {
      test_case_count: evaluationResult.test_case_count || 0,
      execution_time: evaluationResult.execution_time || 0,
      dataset_saved: evaluationResult.dataset_saved || false,
      dataset_location: evaluationResult.dataset_location || 'Unknown',
      cloud_url: evaluationResult.cloud_url || null,
      evaluation_results: evaluationResult.evaluation_results || {},
      ...evaluationResult
    };
    
    // Debug: Log the evaluation result structure
    console.log('EvaluationResultsSection received data:', safeEvaluationResult);
    console.log('Cloud URL value:', safeEvaluationResult.cloud_url);
    console.log('Dataset location:', safeEvaluationResult.dataset_location);
    console.log('Is cloud evaluation:', !safeEvaluationResult.dataset_location?.startsWith('./'));
    
          const downloadResults = () => {
        try {
          const downloadData = {
            evaluation_summary: {
              metric_type: safeEvaluationResult.evaluation_results?.metric_type,
              test_case_count: safeEvaluationResult.test_case_count,
              execution_time: safeEvaluationResult.execution_time,
              dataset_saved: safeEvaluationResult.dataset_saved,
              dataset_location: safeEvaluationResult.dataset_location,
              cloud_url: safeEvaluationResult.cloud_url,
              timestamp: new Date().toISOString()
            },
            detailed_results: safeEvaluationResult.evaluation_results?.detailed_metrics || {},
            raw_data: safeEvaluationResult
          };

        const blob = new Blob([JSON.stringify(downloadData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `deepeval_results_${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error downloading results:', error);
      }
    };

    const getMetricScores = () => {
      try {
        // Try multiple paths to find test cases data
        let testCases = null;
        
        if (evaluationResult.evaluation_results?.detailed_metrics?.testCases) {
          testCases = evaluationResult.evaluation_results.detailed_metrics.testCases;
        } else if (evaluationResult.evaluation_results?.testRunData?.testCases) {
          testCases = evaluationResult.evaluation_results.testRunData.testCases;
        } else if (evaluationResult.testRunData?.testCases) {
          testCases = evaluationResult.testRunData.testCases;
        }

        if (!testCases || !Array.isArray(testCases)) {
          console.log('No test cases found for metric calculation');
          return null;
        }

        console.log('Found test cases for metric calculation:', testCases);

        let passed = 0;
        let failed = 0;
        let errors = 0;

        testCases.forEach((testCase: any, index: number) => {
          console.log(`Test case ${index}:`, testCase);
          
          // Check multiple possible success indicators
          let isSuccess = false;
          
          // Primary: check testCase.success (handle both boolean and string)
          if (testCase.success === true || testCase.success === "True" || testCase.success === "true") {
            isSuccess = true;
          }
          // Secondary: check metricsData success
          else if (testCase.metricsData && Array.isArray(testCase.metricsData)) {
            isSuccess = testCase.metricsData.some((metric: any) => 
              metric.success === true || metric.success === "True" || metric.success === "true"
            );
          }
          // Tertiary: check score threshold
          else if (testCase.metricsData && Array.isArray(testCase.metricsData)) {
            isSuccess = testCase.metricsData.some((metric: any) => 
              metric.score !== undefined && metric.score >= (metric.threshold || 0.7)
            );
          }

          if (isSuccess) {
            passed++;
            console.log(`Test case ${index}: PASSED`);
          } else if (testCase.success === false || testCase.success === "False" || testCase.success === "false") {
            failed++;
            console.log(`Test case ${index}: FAILED`);
          } else {
            errors++;
            console.log(`Test case ${index}: ERROR/UNKNOWN`);
          }
        });

        const total = testCases.length;
        const pass_rate = total > 0 ? (passed / total) * 100 : 0;

        const result = {
          passed,
          failed,
          errors,
          total,
          pass_rate
        };

        console.log('Calculated metric scores:', result);
        return result;
      } catch (error) {
        console.error('Error calculating metric scores:', error);
        return null;
      }
    };

          const getTestCases = () => {
        try {
          // Safely extract test cases with multiple fallback paths
          let testCases = null;
          
          // Try different possible paths for test cases (based on .latest_test_run.json structure)
          if (safeEvaluationResult.evaluation_results?.testRunData?.testCases) {
            testCases = safeEvaluationResult.evaluation_results.testRunData.testCases;
          } else if (safeEvaluationResult.testRunData?.testCases) {
            testCases = safeEvaluationResult.testRunData.testCases;
          } else if (safeEvaluationResult.evaluation_results?.detailed_metrics?.testCases) {
            testCases = safeEvaluationResult.evaluation_results.detailed_metrics.testCases;
          } else if (safeEvaluationResult.evaluation_results?.testCases) {
            testCases = safeEvaluationResult.evaluation_results.testCases;
          } else if (safeEvaluationResult.testCases) {
            testCases = safeEvaluationResult.testCases;
          } else if (safeEvaluationResult.test_cases) {
            testCases = safeEvaluationResult.test_cases;
          }
        
        console.log('getTestCases found:', testCases);
        
        // Ensure testCases is an array
        if (!Array.isArray(testCases)) {
          console.log('testCases is not an array:', testCases);
          return [];
        }
        
        return testCases;
      } catch (error) {
        console.error('Error extracting test cases:', error);
        return [];
      }
    };

    const metricScores = getMetricScores();
    const testCases = getTestCases();
    
    // Fallback metric calculation if primary method fails
    const fallbackMetrics = (() => {
      if (metricScores) return metricScores;
      
      if (testCases && testCases.length > 0) {
        console.log('Fallback metrics: Processing test cases:', testCases);
        let passed = 0;
        testCases.forEach((testCase: any, index: number) => {
          console.log(`Fallback: Test case ${index}:`, testCase);
          console.log(`Fallback: testCase.success = ${testCase.success} (type: ${typeof testCase.success})`);
          
          // Check multiple success indicators
          let isSuccess = false;
          
          if (testCase.success === true || testCase.success === "True" || testCase.success === "true") {
            isSuccess = true;
            console.log(`Fallback: Test case ${index} PASSED via testCase.success`);
          } else if (testCase.metricsData && Array.isArray(testCase.metricsData)) {
            // Check if any metric in metricsData shows success
            const hasSuccessfulMetric = testCase.metricsData.some((metric: any) => 
              metric.success === true || metric.success === "True" || metric.success === "true"
            );
            if (hasSuccessfulMetric) {
              isSuccess = true;
              console.log(`Fallback: Test case ${index} PASSED via metricsData.success`);
            } else {
              // Check score threshold
              const hasGoodScore = testCase.metricsData.some((metric: any) => 
                metric.score !== undefined && metric.score >= (metric.threshold || 0.7)
              );
              if (hasGoodScore) {
                isSuccess = true;
                console.log(`Fallback: Test case ${index} PASSED via score threshold`);
              }
            }
          }
          
          if (isSuccess) {
            passed++;
          }
        });
        
        const total = testCases.length;
        const result = {
          passed,
          failed: total - passed,
          errors: 0,
          total,
          pass_rate: total > 0 ? (passed / total) * 100 : 0
        };
        
        console.log('Fallback metrics result:', result);
        return result;
      }
      
      console.log('Fallback metrics: No test cases found');
      return null;
    })();

      return (
    <div 
      key={`eval-results-${safeEvaluationResult.test_case_count}-${safeEvaluationResult.execution_time}`}
      className={`transition-all duration-500 ease-in-out ${
        isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'
      }`}>
      <Card className="bg-cardbg-900 border-slate-800 text-white mt-10">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-emerald-500" />
              <span>Evaluation Results</span>
              <Badge variant="outline" className="border-emerald-600 text-emerald-400">
                Complete
              </Badge>
            </CardTitle>
          </CardHeader>
          
          <CardContent className="space-y-6">
            {/* Summary Statistics */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-800/50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-white mb-1">
                  {safeEvaluationResult.test_case_count}
                </div>
                <div className="text-sm text-slate-400">Test Cases</div>
              </div>
              
              <div className="bg-slate-800/50 rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-emerald-400 mb-1">
                  {safeEvaluationResult.execution_time?.toFixed(1)}s
                </div>
                <div className="text-sm text-slate-400">Execution Time</div>
              </div>
              
              {fallbackMetrics && (
                <>
                  <div className="bg-slate-800/50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-emerald-400 mb-1">
                      {fallbackMetrics.pass_rate.toFixed(1)}%
                    </div>
                    <div className="text-sm text-slate-400">Pass Rate</div>
                  </div>
                  
                  <div className="bg-slate-800/50 rounded-lg p-4 text-center">
                    <div className="text-2xl font-bold text-slate-400 mb-1">
                      {fallbackMetrics.passed}/{fallbackMetrics.total}
                    </div>
                    <div className="text-sm text-slate-400">Tests Passed</div>
                  </div>
                </>
              )}
              {(() => {
                const hasCloudUrl = Boolean(safeEvaluationResult.cloud_url);
                const isCloudEvaluation = safeEvaluationResult.dataset_location && !safeEvaluationResult.dataset_location.startsWith('./');
                const shouldShowLink = hasCloudUrl || isCloudEvaluation;
                
                console.log('Cloud link decision:', {
                  hasCloudUrl,
                  isCloudEvaluation, 
                  shouldShowLink,
                  dataset_location: safeEvaluationResult.dataset_location,
                  cloud_url: safeEvaluationResult.cloud_url
                });
                
                // If we have a specific cloud URL, use it; otherwise use the generic one for cloud evaluations
                const linkUrl = safeEvaluationResult.cloud_url || 
                               (isCloudEvaluation ? "https://app.confident-ai.com" : null);
                
                return shouldShowLink && linkUrl ? (
                  <a
                    href={linkUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="bg-slate-800/50 border border-emerald-600 rounded-lg p-4 text-center flex items-center space-x-2 hover:bg-blue-950 hover:border-slate-200 transition-colors"
                  >
                    <Cloud className="h-8 w-6" /> 
                    <span className="text-sm">View test results at Confident AI</span>
                  </a>
                ) : null;
              })()}
            </div>

            {/* Metric Information */}
            <div className="bg-slate-800/30 rounded-lg p-4">
              <h4 className="font-medium text-white mb-3 flex items-center space-x-2">
                <Target className="h-4 w-4 text-yellow-500" />
                <span>Metric Details</span>
              </h4>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-slate-400">Metric Type:</span>
                  <span className="ml-2 text-white font-medium capitalize">
                    {safeEvaluationResult.evaluation_results?.metric_type || 'Unknown'}
                  </span>
                </div>
                
                <div>
                  <span className="text-slate-400">Model:</span>
                  <span className="ml-2 text-white font-medium">
                    {safeEvaluationResult.evaluation_results?.model_config?.model_name || 'Unknown'}
                  </span>
                </div>
                
                <div>
                  <span className="text-slate-400">Provider:</span>
                  <span className="ml-2 text-white font-medium capitalize">
                    {safeEvaluationResult.evaluation_results?.model_config?.provider || 'Unknown'}
                  </span>
                </div>
                
                <div>
                  <span className="text-slate-400">Threshold:</span>
                  <span className="ml-2 text-white font-medium">
                    {safeEvaluationResult.evaluation_results?.metric_config?.threshold || 0.7}
                  </span>
                </div>
              </div>
            </div>


            {/* Progress Visualization */}
            {fallbackMetrics && fallbackMetrics.total > 0 && (
              <div className="bg-slate-800/30 rounded-lg p-4">
                <h4 className="font-medium text-white mb-3">Score Distribution</h4>
                
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-slate-400">Pass Rate</span>
                      <span className="text-white">
                        {fallbackMetrics.pass_rate.toFixed(1)}%
                      </span>
                    </div>
                    <Progress 
                      value={fallbackMetrics.pass_rate} 
                      className="h-2 bg-slate-700"
                    />
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div className="text-center">
                      <div className="text-lg font-bold text-emerald-400">{fallbackMetrics.passed}</div>
                      <div className="text-slate-400">Passed</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-red-400">{fallbackMetrics.failed}</div>
                      <div className="text-slate-400">Failed</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-bold text-yellow-400">{fallbackMetrics.errors}</div>
                      <div className="text-slate-400">Errors</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

                      {/* Individual Test Case Results - Collapsible */}
          {testCases && testCases.length > 0 && (
              <Collapsible open={isTestCasesOpen} onOpenChange={setIsTestCasesOpen}>
                <div className="bg-slate-800/30 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <CollapsibleTrigger asChild>
                      <Button
                        variant="ghost"
                        className="flex items-center space-x-2 p-0 h-auto font-medium text-white hover:bg-transparent"
                      >
                                              <h4 className="font-medium text-white">
                        Test Case Results ({testCases.length})
                        </h4>
                        <Badge variant="outline" className="border-emerald-600 text-emerald-400 text-xs">
                          {fallbackMetrics?.passed || 0}/{fallbackMetrics?.total || 0} Passed
                        </Badge>
                        {isTestCasesOpen ? (
                          <ChevronUp className="h-4 w-4 text-slate-400" />
                        ) : (
                          <ChevronDown className="h-4 w-4 text-slate-400" />
                        )}
                      </Button>
                    </CollapsibleTrigger>
                    
                    <Button
                      onClick={downloadResults}
                      variant="outline"
                      size="sm"
                      className="border-slate-800 text-slate-300 hover:bg-gradient-to-r from-cardbg-700 via-zinc-950 to-cardbg-700 hover:border-emerald-700 bg-slate-800 hover:text-white"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download JSON
                    </Button>
                  </div>
                  
                  <CollapsibleContent>
                                      <div className="space-y-3 max-h-96 overflow-y-auto">
                    {testCases.map((testCase: any, index: number) => (
                        <div key={index} className="bg-slate-700/50 rounded-lg p-3 border border-slate-600/50">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-white">Test Case {index + 1}</span>
                            <div className="flex items-center space-x-2">
                              {testCase.success ? (
                                <CheckCircle className="h-4 w-4 text-emerald-500" />
                              ) : (
                                <XCircle className="h-4 w-4 text-red-500" />
                              )}
                              <span className={`text-sm font-bold ${testCase.success ? 'text-emerald-400' : 'text-red-400'}`}>
                                {testCase.metricsData?.[0]?.score ? (testCase.metricsData[0].score * 100).toFixed(1) + '%' : 'N/A'}
                              </span>
                            </div>
                          </div>
                          
                          <div className="text-xs text-slate-400 space-y-2">
                            <div>
                              <span className="font-medium text-slate-300">Input:</span>
                              <div className="mt-1 p-2 bg-slate-800/50 rounded text-slate-300 text-xs max-h-20 overflow-y-auto">
                                {testCase.input}
                              </div>
                            </div>
                            <div>
                              <span className="font-medium text-slate-300">Output:</span>
                              <div className="mt-1 p-2 bg-slate-800/50 rounded text-slate-300 text-xs">
                                {testCase.actualOutput}
                              </div>
                            </div>
                            {testCase.context && testCase.context.length > 0 && (
                              <div>
                                <span className="font-medium text-slate-300">Context:</span>
                                <div className="mt-1 p-2 bg-slate-800/50 rounded text-slate-300 text-xs max-h-16 overflow-y-auto">
                                  {Array.isArray(testCase.context) ? testCase.context.join(' ') : testCase.context}
                                </div>
                              </div>
                            )}
                            {testCase.metricsData?.[0]?.reason && (
                              <div>
                                <span className="font-medium text-emerald-300">Evaluation Reason:</span>
                                <div className="mt-1 p-2 bg-emerald-900/20 border border-emerald-800/50 rounded text-emerald-200 text-xs">
                                  {testCase.metricsData[0].reason}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CollapsibleContent>
                </div>
              </Collapsible>
            )}

            {/* Action Area */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-700">
              <div className="text-sm text-slate-400">
                Evaluation completed at {new Date().toLocaleTimeString()}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  } catch (error) {
    console.error('Error rendering EvaluationResultsSection:', error);
    
    // Fallback rendering in case of errors
    return (
      <div className="transition-all duration-500 ease-in-out opacity-100 translate-y-0">
        <Card className="bg-cardbg-900 border-slate-800 text-white mt-10">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <BarChart3 className="h-5 w-5 text-emerald-500" />
              <span>Evaluation Results</span>
              <Badge variant="outline" className="border-emerald-600 text-emerald-400">
                Complete
              </Badge>
            </CardTitle>
          </CardHeader>
          
          <CardContent className="space-y-6">
            <div className="bg-yellow-900/20 border border-yellow-800 rounded-lg p-4">
              <div className="flex items-center space-x-2 text-yellow-400 mb-2">
                <span className="font-medium">Results Available</span>
              </div>
              <p className="text-sm text-yellow-300">
                Evaluation completed successfully but there was an issue displaying detailed results. 
                Check console logs or use 'deepeval view' to see full results.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }
} 