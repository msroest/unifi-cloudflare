# unifi-cloudflare
Project to pull client IP's from unifi controller and create/remove/update cloudflare dns records.  This is a useful utility when you want your internal dns records to be publicly resolvable.  This can help accessing internal resources when on corporate VPN that takes over DNS.

# Running via Docker
Builds of this utility are published to [Docker Hub](https://hub.docker.com/r/msroest/unifi-cloudflare).  The intention is to run this on a cron schedule at whatever period you desire your DNS to update.

```
docker run -it --rm --env-file environment.env -v <local state storage location>:/state msroest/unifi-cloudflare:latest
```

To exclude specific hostnames from DNS record generation, add a comma-separated list to `UNIFI_EXCLUDE_HOSTNAMES`.
The values are matched against the generated Terraform hostname after the tool's existing sanitization:

```
UNIFI_EXCLUDE_HOSTNAMES=printer01,guest-wifi,lab-pc
```

Due to limitations with the cloudflare terraform provider you will need to delete any existing cloudflare DNS records for records that will be created by this tool.
