FROM mcr.microsoft.com/dotnet/core/sdk:2.1 AS dotnet-build-env

WORKDIR /app

#RUN apt-get install -y dotnet-sdk-2.1
RUN apt-get update

RUN apt-get install -y openssh-server
RUN mkdir /var/run/sshd

RUN echo 'root:citcw200@' |chpasswd

RUN sed -ri 's/^#?PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

RUN mkdir /root/.ssh

#RUN apt-get clean && \    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*


CMD ["/usr/sbin/sshd", "-D"]



#---------------
#service ssh restart
#CMD ["service", "ssh", "restart"]
#EXPOSE 8810
#EXPOSE 443

#FROM microsoft/dotnet:2.1-sdk AS build
#WORKDIR /src
#COPY ["DeIdWeb.csproj", "DeIdWeb/"]
#RUN dotnet restore "DeIdWeb/DeIdWeb.csproj"
COPY . /app
#Run dotnet restore
expose 11065 
#env aspnetcore_urls http://*.8810
entrypoint ["dotnet","run","--server.urls","http://localhost:11065"]
#WORKDIR "/src/DeIdWeb"
#RUN dotnet build "DeIdWeb.csproj" -c Release -o /app

#FROM build AS publish
#RUN dotnet publish "DeIdWeb.csproj" -c Release -o /app

#FROM base AS final
#WORKDIR /app
#COPY --from=publish /app .
#ENTRYPOINT ["dotnet", "DeIdWeb.dll","--server.urls","http://*:8810"]
#ENTRYPOINT ["dotnet", "DeIdWeb.dll"]

#
#FROM microsoft/dotnet:latest AS base
#WORKDIR /app
#EXPOSE 8810
#EXPOSE 443
#
#FROM microsoft/dotnet:2.1-sdk AS build
#WORKDIR /src
#COPY ["DeIdWeb/DeIdWeb.csproj", "DeIdWeb/"]
#RUN dotnet restore "DeIdWeb/DeIdWeb.csproj"
#COPY . .
#WORKDIR "/src/DeIdWeb"
#RUN dotnet build "DeIdWeb.csproj" -c Release -o /app
#
#FROM build AS publish
#RUN dotnet publish "DeIdWeb.csproj" -c Release -o /app
#
#FROM base AS final
#WORKDIR /app
#COPY --from=publish /app .
##ENTRYPOINT ["dotnet", "DeIdWeb.dll","--server.urls","http://*:8810"]
#ENTRYPOINT ["dotnet", "DeIdWeb.dll"]
#


#FROM microsoft/dotnet:latest AS base
#WORKDIR /app
#EXPOSE 8810
#EXPOSE 443

#FROM microsoft/dotnet:2.1-sdk AS build
#WORKDIR /src
#COPY ["DeIdWeb.csproj", "DeIdWeb/"]
#RUN dotnet restore "DeIdWeb/DeIdWeb.csproj"
#COPY . /app
#Run dotnet restore
#expose 8810
#env aspnetcore_urls http://*.8810
#entrypoint ["dotnet","run"]
#WORKDIR "/src/DeIdWeb"
#RUN dotnet build "DeIdWeb.csproj" -c Release -o /app

#FROM build AS publish
#RUN dotnet publish "DeIdWeb.csproj" -c Release -o /app

#FROM base AS final
#WORKDIR /app
#COPY --from=publish /app .
#ENTRYPOINT ["dotnet", "DeIdWeb.dll","--server.urls","http://*:8810"]
#ENTRYPOINT ["dotnet", "DeIdWeb.dll"]
