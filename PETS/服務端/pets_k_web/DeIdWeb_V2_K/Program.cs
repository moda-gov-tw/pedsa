using Microsoft.AspNetCore.Hosting;
using Microsoft.Extensions.Hosting;
using System.IO;
using log4net;
using log4net.Config;
using log4net.Repository;
using Microsoft.AspNetCore;
using System.Xml;
using Microsoft.Extensions.Logging;
using System.Security.Authentication;

[assembly: log4net.Config.XmlConfigurator(ConfigFile = "log4net.config", Watch = true)]
namespace DeIdWeb_V2_K
{
    public class Program
    {
        private static ILoggerRepository _loggerRepository;
        //static ILog logger = LogManager.GetLogger(typeof(Program));
        //static ILog logger;
        public static void Main(string[] args)
        {
            _loggerRepository = LogManager.CreateRepository("DeIdWeb");
            XmlConfigurator.ConfigureAndWatch(_loggerRepository, new FileInfo("log4net.config"));
            var log = LogManager.GetLogger(_loggerRepository.Name, typeof(Program));
            CreateHostBuilder(args).Build().Run();
        }

        public static IHostBuilder CreateHostBuilder(string[] args) =>
            Host.CreateDefaultBuilder(args)
        //.ConfigureLogging((context, logger) =>
        //{
        //    logger.AddFilter("System", LogLevel.Warning); //�L�o��System
        //    logger.AddFilter("Microsoft", LogLevel.Warning);//�L�o��Microsoft
        //    logger.AddLog4Net();//�s�W��x --�o�@�B�ܫܭ��n�A�_�h�L�k�g�J��x
        //})


        //.ConfigureWebHostDefaults(webBuilder =>
        //{
        //    //.UseUrls("http://+ :11000")
        //    webBuilder.UseStartup<Startup>();
        //    webBuilder.UseKestrel(options =>
        //    {
        //        // var sslCertPath = Path.Combine(AppContext.BaseDirectory, "ssl.pfx");

        //        options.ConfigureHttpsDefaults(co =>
        //        {
        //            co.SslProtocols = SslProtocols.Tls12;
        //        });

        //    });
        //    webBuilder.UseUrls("https://+ :11000");
        //});

        //http version
        .ConfigureWebHostDefaults(webBuilder =>
        {
            // �]�m Startup ��
            webBuilder.UseStartup<Startup>();

            // �ϥ� Kestrel ���A���A���t�m HTTPS
            webBuilder.UseKestrel();

            // �]�m HTTP URL
            webBuilder.UseUrls("http://+:11000");
        });

    }
}
