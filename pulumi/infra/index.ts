import * as pulumi from "@pulumi/pulumi"
import * as gcp from "@pulumi/gcp"

// Create a GCP resource (Storage Bucket)
const aboutBucket = new gcp.storage.Bucket('aboutBucket', {
    name: 'hugo-about-me-static',
    forceDestroy: true,
    cors: [{
        maxAgeSeconds: 3600,
        methods: [
            'GET',
            'HEAD',
            'PUT',
            'POST',
            'DELETE',
        ],
        origins: ['http://qgriffith.com', 'https://qgriffith.com'],
        responseHeaders: ['*'],
    }],
    location: 'US',
    uniformBucketLevelAccess: true,
    
    website: {
        mainPageSuffix: 'index.html',
        notFoundPage: '404.html'
    }   
})

const aboutdefaultGlobalAddress = new gcp.compute.GlobalAddress("aboutdefaultGlobalAddress", {
    name: 'aboutip'
})

const aboutManagedSslCertificate = new gcp.compute.ManagedSslCertificate("aboutManagedSslCertificate", {
    name: 'abouttls',
    description: 'about-me ssl',
    managed: {
        domains: ['qgriffith.com.'],
    }
})

const aboutBucketIAMBinding = new gcp.storage.BucketIAMBinding('aboutBucketIAMBinding', {
    bucket: aboutBucket.name,
    role: 'roles/storage.objectViewer',
    members: ['allUsers']
})

const aboutHttpHealthCheck = new gcp.compute.HttpHealthCheck('aboutHttpHealthCheck', {
    name: 'abouthttphealth',
    requestPath: '/',
    checkIntervalSec: 1,
    timeoutSec: 1
})

const aboutBackend = new gcp.compute.BackendBucket('aboutBackend', {
    name: 'aboutbackend',
    description: 'About Me Hugo Backend',
    bucketName: aboutBucket.name,
    enableCdn: true
})

const aboutDefaultURLMap = new gcp.compute.URLMap('aboutDefaultURLMap', {
    name: 'aboutmap',
    description: 'About me map all',
    defaultService: aboutBackend.id,
    hostRules: [{
        hosts: ['qgriffith.com'],
        pathMatcher: 'allpaths',
    }],
    pathMatchers: [{
        name: 'allpaths',
        defaultService: aboutBackend.id,
        pathRules: [{
            paths: ["/*"],
            service: aboutBackend.id,
        }],
    }],
})

const aboutRedirectMap = new gcp.compute.URLMap('aboutRedirectMap',{
    name: 'aboutredirectmap',
    description: 'redirect http-to-https',
    defaultUrlRedirect: {
        httpsRedirect: true,
        stripQuery: false,
        redirectResponseCode: 'MOVED_PERMANENTLY_DEFAULT'
    }
})

const aboutDefaultTargetHttsproxy = new gcp.compute.TargetHttpsProxy('aboutDefaultTargetHttpProxy', {
    name: 'aboutme',
    urlMap: aboutDefaultURLMap.id,
    sslCertificates: [ aboutManagedSslCertificate.id ]
})

const aboutDefaultTargetRedirectProxy = new gcp.compute.TargetHttpProxy('aboutDefaultTargetRedirectProxy', {
    name: 'aboutmeredirect',
    urlMap: aboutRedirectMap.id
})

const aboutForwardRule = new gcp.compute.GlobalForwardingRule('aboutForwardRule', {
    name: 'aboutforwardrule',
    description: 'About-me forward to bucket',
    portRange: "443",
    target: aboutDefaultTargetHttsproxy.id,
    ipAddress: aboutdefaultGlobalAddress.id
})

const aboutRedirectRule = new gcp.compute.GlobalForwardingRule('aboutRedirectRule', {
    name: 'aboutredirectrule',
    description: 'About-me http-to-https',
    portRange: "80",
    target: aboutDefaultTargetRedirectProxy.id,
    ipAddress: aboutdefaultGlobalAddress.id
})


// Export the DNS name of the bucket
export const aboutBucketUrl = aboutBucket.url
export const aboutdefaultGlobalAddressId = aboutdefaultGlobalAddress.id
export const aboutBucketIAMBindingId = aboutBucketIAMBinding.id
export const aboutManagedSslCertificateId = aboutManagedSslCertificate.id
export const aboutHealthCheckId = aboutHttpHealthCheck.id
export const aboutBackEndId = aboutBackend.id
export const aboutDefaultURLMapId = aboutDefaultURLMap.id
export const aboutRedirectMapId = aboutRedirectMap.id
export const aboutDefaultTargetHttpsProxyId = aboutDefaultTargetHttsproxy.id
export const aboutDefaultTargetRedirectProxyId = aboutDefaultTargetRedirectProxy.id
export const aboutForwardRuleId = aboutForwardRule.id
export const aboutForwardRuleIP = aboutForwardRule.ipAddress
export const aboutRedirectRuleId = aboutRedirectRule.id
export const aboutRedirectRuleIp = aboutRedirectRule.ipAddress
