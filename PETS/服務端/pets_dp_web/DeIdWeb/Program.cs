using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using DeIdWeb.Infrastructure.Reposiotry;
using log4net;
using log4net.Config;
using log4net.Repository;
using Microsoft.AspNetCore;
using Microsoft.AspNetCore.Hosting;


namespace DeIdWeb
{
    public class Program
    {
        //log4Net
        private static ILoggerRepository _loggerRepository;
        public static void Main(string[] args)
        {
            //_loggerRepository = LogManager.CreateRepository("SynDeId");
            _loggerRepository = LogManager.CreateRepository("DpDeId");
            XmlConfigurator.ConfigureAndWatch(_loggerRepository, new FileInfo("log4net.config"));
            var log = LogManager.GetLogger(_loggerRepository.Name, typeof(Program));
           
            CreateWebHostBuilder(args).Build().Run();
        }

        public static IWebHostBuilder CreateWebHostBuilder(string[] args) =>
            WebHost.CreateDefaultBuilder(args)
            //.ConfigureLogging((hostingContext,logging) =>
            //{
            //    logging.AddFilter("System",LogLevel.Warning);
            //    logging.AddFilter("Microsoft",LogLevel.Warning);
            //    logging.AddLog4Net();
            //})
            //.UseUrls("http://+ :5000", "http://+ :11000")
            .UseUrls("http://+ :11065")
                .UseStartup<Startup>();
    }
}
