﻿using System;
using System.IO;
using log4net;
using log4net.Config;
using log4net.Repository;

namespace DeIdWeb.Infrastructure.Reposiotry
{
    public class DeIdLogManager
    {
        public DeIdLogManager()
        {
        }

        private static ILoggerRepository _loggerRepository;

        /// <summary>
        /// 启动logger
        /// </summary>
        /// <param name="repository">repository名称</param>
        /// <param name="fileName">配置文件名称</param>
        public static void StartLogger(string repository, string fileName)
        {
            _loggerRepository = LogManager.CreateRepository(repository);
            XmlConfigurator.ConfigureAndWatch(_loggerRepository, new FileInfo(fileName));
        }

        /// <summary>
        /// 启动logger
        /// </summary>
        public static void StartLogger()
        {
            _loggerRepository = LogManager.CreateRepository(nameof(DeIdLogManager));
            XmlConfigurator.ConfigureAndWatch(_loggerRepository, new FileInfo("log4net.config"));
        }

        public static ILog GetMyLog<T>(T t)
        {
            return LogManager.GetLogger(_loggerRepository.Name, t.GetType());
        }

        public static ILog GetMyLog(object obj)
        {
            return LogManager.GetLogger(_loggerRepository.Name, obj.GetType());
        }

        public static ILog GetMyLog(Type type)
        {
            return LogManager.GetLogger(_loggerRepository.Name, type);
        }
    }
}