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
        origins: ['http://qgriffith.com'],
        responseHeaders: ['*'],
    }],
    location: 'US',
    uniformBucketLevelAccess: true,
    
    website: {
        mainPageSuffix: 'index.html',
        notFoundPage: '404.html'
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

const aboutDefaultTargetHttpProxy = new gcp.compute.TargetHttpProxy('aboutDefaultTargetHttpProxy', {
    name: 'aboutme',
    urlMap: aboutDefaultURLMap.id
});

const aboutForwardRule = new gcp.compute.GlobalForwardingRule('aboutForwardRule', {
    name: 'aboutforwardrule',
    description: 'About-me forward to bucket',
    portRange: "80",
    target: aboutDefaultTargetHttpProxy.selfLink
})


// Export the DNS name of the bucket
export const aboutBucketUrl = aboutBucket.url
export const aboutBucketIAMBindingId = aboutBucketIAMBinding.id
export const aboutHealthCheckId = aboutHttpHealthCheck.id
export const aboutBackEndId = aboutBackend.id
export const aboutDefaultURLMapId = aboutDefaultURLMap.id
export const aboutDefaultTargetHttpProxyId = aboutDefaultTargetHttpProxy.id
export const aboutForwardRuleId = aboutForwardRule.id
