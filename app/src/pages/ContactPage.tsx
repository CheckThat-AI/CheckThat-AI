import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Checkbox } from '@/components/ui/checkbox';
import { Mail, MessageSquare, CheckCircle, Send } from 'lucide-react';
import emailjs from '@emailjs/browser';
import { Toaster, toast } from 'react-hot-toast';
import discordLogo from "../assets/discord-logo.svg";
// import linkedinLogo from "../assets/linkedin-logo.svg";
import slackLogo from "../assets/slack-logo.svg";

const ContactPage = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [errors, setErrors] = useState<{[key: string]: string}>({});
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
    newsletter: false
  });

  const validate = () => {
    const validationErrors: {[key: string]: string} = {};
    if (!formData.name.trim()) validationErrors.name = "Name is required";
    if (!formData.email.trim()) {
      validationErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      validationErrors.email = "Email is invalid";
    }
    if (!formData.subject.trim()) validationErrors.subject = "Subject is required";
    if (!formData.message.trim()) validationErrors.message = "Message is required";
    return validationErrors;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const validationErrors = validate();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      return;
    }
    
    setErrors({});
    setIsSubmitting(true);
    
    try {
      // Send email using EmailJS
      await emailjs.send(
        "service_3hqot5c", // EmailJS service ID
        "template_l19k1uk", // EmailJS template ID
        {
          from_name: formData.name,
          from_email: formData.email,
          subject: formData.subject,
          message: formData.message,
          newsletter: formData.newsletter ? "Yes" : "No",
          reply_to: formData.email,
          to_email: "support@checkthat-ai.com", // Your email address
        },
        "3Q0HSwhn1mJZ0w6O6" // EmailJS User ID
      );
      
      toast.success("Message sent successfully!");
      setSubmitted(true);
      
      // Reset form after 3 seconds
      setTimeout(() => {
        setSubmitted(false);
        setFormData({
          name: '',
          email: '',
          subject: '',
          message: '',
          newsletter: false
        });
      }, 3000);
      
    } catch (error) {
      console.error("Failed to send email:", error);
      toast.error("Failed to send message. Please try again later.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  return (
    <div id="contact" className="w-full bg-gradient-to-br from-slate-50 to-slate-100 dark:bg-gradient-to-tl dark:from-background dark:via-zinc-950 dark:to-zinc-800 backdrop-blur-sm">
      <Toaster position="top-right" />
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid lg:grid-cols-2 gap-8">
            {/* Left Side - Contact Cards */}
            <div className="space-y-6">
                {/* Header Section */}
                <Card className="text-center mb-10 bg-white border-slate-200 dark:bg-gradient-to-tl dark:from-zinc-950 dark:to-zinc-800 dark:border-slate-700 backdrop-blur-sm">
                    <CardHeader className="inline-block px-4 py-2 text-blue-600 dark:text-blue-400 max-w-full text-sm">
                        <CardTitle className="text-lg font-semibold">
                            CUSTOMER FEEDBACK
                        </CardTitle>
                    </CardHeader>
                    <CardContent className="text-md font-bold text-slate-900 dark:text-white mb-8">
                        Early Customers Feedback
                        {/* Feature Points */}
                        <div className="max-w-2xl mx-auto space-y-4 mt-6">
                            <div className="flex items-center justify-center text-left">
                                <div className="text-blue-600 dark:text-blue-400 mr-3">✦</div>
                                <span className="text-slate-700 dark:text-slate-300">Hassle-Free Support: Link with our crew anytime</span>
                            </div>
                            <div className="flex items-center justify-center text-left">
                                <div className="text-blue-600 dark:text-blue-400 mr-3">✦</div>
                                <span className="text-slate-700 dark:text-slate-300">Schedule a Demo Now: Witness our platform's performance</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>

                {/* Contact Methods */}
                <Card className="bg-white border-slate-200 dark:bg-slate-800/50 dark:border-slate-700 backdrop-blur-sm 
                dark:bg-gradient-to-l dark:from-zinc-950 dark:to-zinc-800">
                    <CardHeader className="pb-2">
                        <div className="flex items-center mb-2">
                            <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mr-4">
                                <MessageSquare className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                            </div>
                            <CardTitle className="text-xl text-slate-900 dark:text-white">
                                Reach Out to Us
                            </CardTitle>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <p className="text-slate-700 dark:text-slate-300 mb-8 text-xl">
                            Have questions? We're here to help reach out!
                        </p>
                        <Button 
                            variant="outline" 
                            className="w-full border-slate-300 text-slate-300 hover:bg-slate-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-700"
                            onClick={() => window.open('mailto:nikhil.kadapala@checkthat-ai.com')}
                        >
                            <Mail className="w-4 h-4 mr-2" />
                            support@checkthat-ai.com
                        </Button>
                        <div className="flex items-center mt-8">
                            <a href="https://discord.gg/3wWspbaS" target="_blank" rel="noopener noreferrer">
                                <img src={discordLogo} className="w-10 h-10 mx-2 cursor-pointer" alt="Discord Logo" />
                            </a>
                            {/* <a href="https://linkedin.com/in/nikhil-kadapala" target="_blank" rel="noopener noreferrer">
                                <img src={linkedinLogo} className="w-10 h-10 mx-2 cursor-pointer" alt="LinkedIn Logo" />
                            </a> */}
                            <a href="https://join.slack.com/t/checkthatai/shared_invite/zt-3a76srzs3-6Aku535esqBCyNeXUWNdAg" target="_blank" rel="noopener noreferrer">
                                <img src={slackLogo} className="w-10 h-10 mx-2 cursor-pointer" alt="Slack Logo" />
                            </a>
                        </div>
                    </CardContent>
                </Card>
            </div>

            {/* Right Side - Contact Form */}
            <Card className="bg-white border-slate-200 dark:bg-gradient-to-tl dark:from-background dark:via-zinc-950 dark:to-zinc-800 dark:border-slate-700 backdrop-blur-sm">
              <CardContent className="p-8">
                {submitted ? (
                  <div className="text-center py-12">
                    <CheckCircle className="w-16 h-16 text-green-600 dark:text-green-400 mx-auto mb-4" />
                    <h3 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">
                      Message Sent Successfully!
                    </h3>
                    <p className="text-slate-700 dark:text-slate-300">
                      Thank you for reaching out. We'll get back to you soon.
                    </p>
                  </div>
                ) : (
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Name Field */}
                    <div className="space-y-2">
                      <Label htmlFor="name" className="text-slate-700 dark:text-slate-300">
                        Name
                      </Label>
                      <Input
                        id="name"
                        name="name"
                        type="text"
                        placeholder="Jason Bourne"
                        value={formData.name}
                        onChange={handleInputChange}
                        className="bg-slate-50 border-slate-300 text-slate-900 placeholder:text-slate-500 dark:bg-slate-700/50 dark:border-slate-600 dark:text-white dark:placeholder:text-slate-400"
                        required
                      />
                      {errors.name && (
                        <p className="text-sm text-red-500 dark:text-red-400 font-medium">
                          {errors.name}
                        </p>
                      )}
                    </div>

                    {/* Email Field */}
                    <div className="space-y-2">
                      <Label htmlFor="email" className="text-slate-700 dark:text-slate-300">
                        Email
                      </Label>
                      <Input
                        id="email"
                        name="email"
                        type="email"
                        placeholder="jason.bourn@cia.gov"
                        value={formData.email}
                        onChange={handleInputChange}
                        className="bg-slate-50 border-slate-300 text-slate-900 placeholder:text-slate-500 dark:bg-slate-700/50 dark:border-slate-600 dark:text-white dark:placeholder:text-slate-400"
                        required
                      />
                      {errors.email && (
                        <p className="text-sm text-red-500 dark:text-red-400 font-medium">
                          {errors.email}
                        </p>
                      )}
                    </div>

                    {/* Subject Field */}
                    <div className="space-y-2">
                      <Label htmlFor="subject" className="text-slate-700 dark:text-slate-300">
                        Subject of Interest
                      </Label>
                      <Input
                        id="subject"
                        name="subject"
                        type="text"
                        placeholder="Product related"
                        value={formData.subject}
                        onChange={handleInputChange}
                        className="bg-slate-50 border-slate-300 text-slate-900 placeholder:text-slate-500 dark:bg-slate-700/50 dark:border-slate-600 dark:text-white dark:placeholder:text-slate-400"
                        required
                      />
                      {errors.subject && (
                        <p className="text-sm text-red-500 dark:text-red-400 font-medium">
                          {errors.subject}
                        </p>
                      )}
                    </div>

                    {/* Message Field */}
                    <div className="space-y-2">
                      <Label htmlFor="message" className="text-slate-700 dark:text-slate-300">
                        Message
                      </Label>
                      <Textarea
                        id="message"
                        name="message"
                        placeholder="Feel free to share your Feedback or drop any queries..."
                        value={formData.message}
                        onChange={handleInputChange}
                        className="bg-slate-50 border-slate-300 text-slate-900 placeholder:text-slate-500 dark:bg-slate-700/50 dark:border-slate-600 dark:text-white dark:placeholder:text-slate-400 min-h-[120px]"
                        required
                      />
                      {errors.message && (
                        <p className="text-sm text-red-500 dark:text-red-400 font-medium">
                          {errors.message}
                        </p>
                      )}
                    </div>

                    {/* Newsletter Checkbox */}
                    <div className="flex items-center space-x-2">
                      <Checkbox
                        id="newsletter"
                        checked={formData.newsletter}
                        onCheckedChange={(checked: boolean) => 
                          setFormData(prev => ({ ...prev, newsletter: checked }))
                        }
                        className="border-slate-400 data-[state=checked]:bg-blue-600 data-[state=checked]:border-blue-600 dark:border-slate-600 dark:data-[state=checked]:bg-blue-500 dark:data-[state=checked]:border-blue-500"
                      />
                      <Label
                        htmlFor="newsletter"
                        className="text-slate-700 dark:text-slate-300 text-sm cursor-pointer"
                      >
                        Subscribe to Newsletter
                      </Label>
                    </div>

                    {/* Submit Button */}
                    <Button
                      type="submit"
                      disabled={isSubmitting}
                      className="w-full bg-blue-600 hover:bg-blue-700 dark:bg-blue-600 dark:hover:bg-blue-700 text-white py-3 text-lg font-medium"
                    >
                      {isSubmitting ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2" />
                          Sending...
                        </>
                      ) : (
                        <>
                          <Send className="w-4 h-4 mr-2" />
                          Submit
                        </>
                      )}
                    </Button>
                  </form>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactPage;
