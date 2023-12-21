#See https://aka.ms/containerfastmode to understand how Visual Studio uses this Dockerfile to build your images for faster debugging.

#FROM mcr.microsoft.com/dotnet/aspnet:3.1 AS base
FROM mcr.microsoft.com/dotnet/core/sdk:3.1 AS build
WORKDIR app
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

# copy csproj and restore as distinct layers
COPY *.csproj ./
RUN dotnet restore

# copy everything else and build app
COPY . ./
RUN dotnet publish -c Release -o out


#FROM mcr.microsoft.com/dotnet/core/aspnet:3.1 AS final 
ENV ASPNETCORE_URLS=https://+:11000
WORKDIR /app
EXPOSE 11000/tcp
#COPY --from=build /app/out .
#ENTRYPOINT ["dotnet", "DeIdWeb_V2.dll"]
entrypoint ["dotnet","run","--server.urls","https://localhost:11000"]
#FROM mcr.microsoft.com/dotnet/sdk:3.1 AS build
#WORKDIR /src
#COPY ["../DeIdWeb_V2/DeIdWeb_V2.csproj", "DeIdWeb_V2/"]
#RUN dotnet restore "DeIdWeb_V2/DeIdWeb_V2.csproj"
#COPY . .
#WORKDIR "/src/DeIdWeb_V2"
#RUN dotnet build "DeIdWeb_V2.csproj" -c Release -o /app/build
#
#FROM build AS publish
#RUN dotnet publish "DeIdWeb_V2.csproj" -c Release -o /app/publish
#
#FROM base AS final
#WORKDIR /app
#COPY --from=publish /app/publish .
##ENTRYPOINT ["dotnet", "DeIdWeb_V2.dll"]
#entrypoint ["dotnet","run","--server.urls","http://localhost:11000"]
#
