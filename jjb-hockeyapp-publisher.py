def hockeyapp(parser, xml_parent, data):
    """yaml: hockeyapp
    Publisher that uses HockeyApp plugin.
    Requires the Jenkins :jenkins-wiki:`HockeyApp Plugin
    <HockeyApp Plugin>`.

    :arg str api-token: Your HockeyApp API Token (default "")
    :arg bool upload-app: Upload app. (default true)
    :arg str app-id: Upload specific app. Provide app id.
    :arg str file-path: The path, relative to the build's workspace,
        to the generated .ipa (iOS), .app.zip (MacOS), or .apk (Android) file.
    :arg str symbols: An optional path, relative to the build's workspace,
        to the generated dSYM.zip (iOS and MacOS) or mapping.txt
        (Android) file.
    :arg str packed-libraries: Optional path, relative to the build's
        workspace, to an archive with generated .so files. This
        archive must have the following structure:
        ${ARCHITECTURE}/*.so
    :arg dict release-notes:
        :arg bool no-release-notes: No Release Notes (true)
        :arg bool use-change-log: Use Change Log (false)
        :arg dict from-file:
            :from-file:
                * **filename** (`str`) -- Release notes filename
                * **interpret-release-notes-as-markdown** (`bool`) -- If
                   checked HockeyApp expectes the provided Release notes
                   to be written in Markdown.
        :arg dict input:
            :input:
                * **rel-notes-text** (`str`)
                * **interpret-release-notes-as-markdown** (`bool`) -- If
                   checked HockeyApp expectes the provided Release notes
                   to be written in Markdown.

    :arg bool allow-downloads: Enable if you want new versions to be available
        for download and installation immediately, without having to enable
        this manually in HockeyApp. (false)
    :arg str restrict-downloads-to-tags: By entering a comma-separated list
        of tags here, you can restrict downloads of your app to only
        users/devices with these tags. (default "")
    :arg bool notify-team: Enable if you want HockeyApp to notify your team
        about each uploaded version. (false)
    :arg str delete-old-versions: Number of old versions to keep on HockeyApp.
        (default "")
    :arg bool enable-debug-mode: Enables debug mode. (false)
    :arg bool fail-gracefully: If the upload to HockeyApp fails, the build
        is not marked as failed once fail gracefully is enabled. (false)
    :arg str custom-hockeyapp-api-url: Please insert an alternate Host-URL
        for the Hockey-App Service. (default '')

    Example:

    .. literalinclude:: /../../tests/publishers/fixtures/hockeyapp001.yaml
       :language: yaml
    """

    recorder = XML.SubElement(
                              xml_parent, 
                              'hockeyapp.HockeyappRecorder',
                              {'schemaVersion': '2'})
    applications = XML.SubElement(recorder, 'applications')
    hockeyapp = XML.SubElement(
                               applications,
                               'hockeyapp.HockeyappApplication',
                               {'plugin': 'hockeyapp@1.2.0', 'schemaVersion': '1'})

    # notify-team
    XML.SubElement(hockeyapp, 'notifyTeam').text = str(
        data.get('notify-team', False)).lower()
    # Add apiToken only if defined
    if 'apiToken' in data:
        XML.SubElement(hockeyapp, 'apiToken').text = str(
            data['api-token'])
    # filePath
    if 'file-path' not in data:
        raise JenkinsJobsException("You have not specified"
                                   " file-path parameter.")
    XML.SubElement(hockeyapp, 'filePath').text = str(
        data.get('file-path', ''))
    # Allow Downloads
    XML.SubElement(hockeyapp, 'downloadAllowed').text = str(
        data.get('allow-downloads', False)).lower()
    # dsymPath
    if 'symbols' in data:
        XML.SubElement(hockeyapp, 'dsymPath').text = str(
            data.get('symbols', ''))
    # libsPath
    if 'packed-libraries' in data:
        XML.SubElement(hockeyapp, 'libsPath').text = str(
            data.get('packed-libraries', ''))
    #### Release Notes
    if 'release-notes' in data:
        try:
            rdata = iter(data['release-notes'])
        except:
            raise JenkinsJobsException("You have to specify at least"
                                       " one option for release-notes.")

        rdata = data['release-notes']
        if 'no-release-notes' in rdata and ('use-change-log' in rdata
            or 'from-file' in rdata or 'input' in rdata):
            raise JenkinsJobsException("You cannot specify more"
                                       " than one release-notes options.")
        if 'use-change-log' in rdata and ('no-release-notes' in rdata
            or 'from-file' in rdata or 'input' in rdata):
            raise JenkinsJobsException("You cannot specify more"
                                       " than one release-notes options.")
        if 'no-release-notes' in rdata:
            XML.SubElement(
                hockeyapp,
                'releaseNotesMethod',
                {'class': 'net.hockeyapp.jenkins.releaseNotes.NoReleaseNotes'})
        elif 'use-change-log' in rdata:
            XML.SubElement(
                hockeyapp,
                'releaseNotesMethod',
                {'class': 'net.hockeyapp.jenkins.releaseNotes.ChangelogReleaseNotes'})
        elif 'from-file' in rdata:
            relnotes = XML.SubElement(
                hockeyapp,
                'releaseNotesMethod',
                {'class': 'net.hockeyapp.jenkins.releaseNotes.FileReleaseNotes'})
            nrdata = rdata['from-file']
            mandatory = 0
            for key in nrdata:
                if 'filename' in key:
                    XML.SubElement(relnotes, 'fileName').text = str(
                        key.get('filename', 'False'))
                    mandatory = 1
                XML.SubElement(relnotes, 'isMarkdown').text = str(
                    key.get('interpret-release-notes-as-markdown', False)).lower()
            if mandatory != 1:
                raise JenkinsJobsException("filename must be defined"
                                           " when from-file option is present.")
        elif 'input' in rdata:
            relnotes = XML.SubElement(
                hockeyapp,
                'releaseNotesMethod',
                {'class': 'net.hockeyapp.jenkins.releaseNotes.ManualReleaseNotes'})
            nrdata = rdata['input']
            for key in nrdata:
                if 'rel-notes-text' in key:
                    XML.SubElement(relnotes, 'releaseNotes').text = str(
                        key.get('rel-notes-text', ''))
                XML.SubElement(relnotes, 'isMarkdown').text = str(
                    key.get('interpret-release-notes-as-markdown', False)).lower()
    # Upload method App/Version
    if 'upload-app' in data and 'app-id' in data:
        raise JenkinsJobsException("You cannot specify both app"
                                   " and version methods")
    if 'app-id' not in data:
        XML.SubElement(
            hockeyapp,
            'uploadMethod',
            {'class': 'net.hockeyapp.jenkins.uploadMethod.AppCreation'})
    else:
        method = XML.SubElement(
            hockeyapp,
            'uploadMethod',
            {'class': 'net.hockeyapp.jenkins.uploadMethod.VersionCreation'})
        XML.SubElement(method, 'appId').text = str(
            data.get('app-id', ''))
    # Restrict Downloads to Tags
    if 'restrict-downloads-to-tags' in data:
        XML.SubElement(hockeyapp, 'tags').text = str(
            ",".join(data['restrict-downloads-to-tags']))
    # delete old versions
    if 'delete-old-versions' in data:
        version_holder = XML.SubElement(hockeyapp, 'oldVersionHolder')
        XML.SubElement(version_holder, 'numberOldVersions').text = str(
            data.get('delete-old-versions', '1'))
    # DEBUG MODE
    XML.SubElement(recorder, 'debugMode').text = str(
        data.get('enable-debug-mode', False)).lower()
    # FAIL GRACEFULLY
    XML.SubElement(recorder, 'failGracefully').text = str(
        data.get('fail-gracefully', False)).lower()
    # custom-hockeyapp-api-url
    if 'custom-hockeyapp-api-url' in data:
        XML.SubElement(recorder, 'baseUrl').text = str(
            data.get('custom-hockeyapp-api-url', False))
