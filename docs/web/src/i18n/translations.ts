import type { Language } from '../context/LanguageContext';

export const translations = {
    en: {
        // Navbar
        nav: {
            main: 'Main',
            menu: 'Menu',
            documentation: 'Docs',
            showcase: 'Showcase',
            playground: 'Playground',
            tools: 'Tools',
            switchLanguage: 'Passer en français',
            themeSystem: 'Theme: same as your system',
            themeLight: 'Theme: light',
            themeDark: 'Theme: dark',
        },

        // Hero Section
        hero: {
            releasedDaysAgo: 'released {n} days ago',
            releasedToday: 'released today',
            releasedYesterday: 'released yesterday',
            license: 'MIT licensed',
            title: 'Custom items and blocks without writing every file',
            subtitle: 'Define an item or a block once. StewBeet writes its models, recipes, loot tables, translations and manual page on every build. The commands you still write by hand are checked by Spyglass in VS Code.',
            readQuickstart: 'Read the quickstart',
            browseDocs: 'Browse the docs',
            newToPython: 'New to Python?',
            newToPythonText: 'A definition is a name, some values and a recipe. If you can read datapack JSON, you can read one.',
            proofTitle: 'One block, defined once',
            codeCaption: 'definitions/additions/equipments.py',
            writtenByBuild: 'Written by the build:',
            blockFunctions: 'Block functions: {n}',
            crafterRecipes: 'Smithed Crafter recipes: {n}',
            lootTables: 'Loot tables: {n}',
            manualPages: 'Manual pages: {n}',
            resourcePackFiles: 'Resource pack files: {n}',
            proofCaption: '{n} files from this one definition. The first slot holds the render the build makes for the in-game manual.',
            replay: 'Play the build again',
            ingameCaption: 'In game, Minecraft 26.3',
            ingameAlt: 'The Life Crystal Block placed in a Minecraft world',
        },

        // A user quote, beside the objection it answers
        testimonial: {
            casperQuote: "I didn't know any Python, but thanks to a lot of trial and error I was able to figure it out, and it's been great.",
            casperCaption: 'made their first custom blocks with StewBeet',
            translated: '',
        },

        // The proof that the generated files stay readable, beside the user who feared they would not
        control: {
            title: 'You keep control of every file',
            text: 'The build writes plain datapack and resource pack files, and heads each function with where it is called from. Here are the {n} files of the block above, as the build wrote them.',
            sourceMaps: 'Source maps link each line to the Python that wrote it.',
            files: 'Files written from the block',
            racoonQuote: 'Before trying it, I was pretty wary of pre-compilers: I thought all that abstraction would turn into spaghetti code. But StewBeet fits right into the creative process. It takes care of lots of tasks that add up to lost time and mental fatigue, while keeping absolute control over the code you produce.',
            racoonCaption: 'author of',
            translated: 'translated from French',
        },

        // Copy buttons
        copy: {
            action: 'Copy',
            copied: 'Copied',
            command: 'Copy the command',
        },

        // What one definition saves
        gains: {
            title: 'One block by hand is eight files',
            lead: 'In two packs and four formats. Miss one and nothing errors: the block never drops. StewBeet writes all eight from the definition on every build.',
            byHand: 'By hand',
            withStewbeet: 'With StewBeet',
            withUnit: 'definition to maintain',
            withNote: 'The eight files are written from it on every build, so they never drift apart.',
            materialsTitle: 'One material, the whole tier',
            materialsText: 'Name an ingot and the vanilla tier it matches. The tools, armour, ore, block and nugget come from the textures you dropped in, recipes included.',
            materialsAlt: "Stardust Fragment's solarium ingot, and the tools, armour and block registered from it",
            langTitle: 'Your text, ready to translate',
            langText: 'Write plain text in your commands. The build turns each one into a translation key and collects them in en_us.json.',
            langBefore: 'What you write',
            langAfter: 'What the build writes',
        },

        // In-game manual showcase
        manual: {
            title: 'Your datapack documents itself',
            description: 'Every item you define gets a manual page: its recipe drawn from the ingredients you declared, its description, and links between categories. Players craft the book in game, and the next build updates it.',
            readMore: 'How the manual works',
            videoFallback: 'Your browser cannot play this video.',
        },

        // Editor showcase
        editor: {
            title: 'Your commands, checked in your editor',
            description: 'A command inside a Python string is still a command. The StewBeet extension for VS Code gives it completion, hover and errors as you type, and Ctrl+click goes from a write_function call to the file the build wrote.',
            install: 'Get it on the marketplace',
            readMore: 'What it does',
            videoFallback: 'Your browser cannot play this video.',
        },

        // Trust strip
        trust: {
            label: 'Project activity',
            downloadsPerMonth: 'PyPI downloads a month',
            publicProjects: 'public projects built with it',
            githubStars: 'GitHub stars',
        },

        // Built with StewBeet
        builtWith: {
            title: '{n} public projects are built with StewBeet',
            subtitle: "Other datapackers' projects first, then the author's packs and libraries. Each card opens its source.",
            community: 'community',
            previous: 'Previous projects',
            next: 'Next projects',
            filesFrom: '{files} files from {lines} lines of Python',
            seeAll: 'See them all.',
        },

        // The /showcase page
        showcase: {
            lead: 'Datapacks, games and libraries with public source. Each card opens it, so you can read how a real project lays out its definitions.',
            community: 'By the community',
            packs: "By StewBeet's author",
            libraries: 'Libraries',
            addTitle: 'Add yours',
            addText: 'Built something with StewBeet and published its source?',
            addLink: 'Open an issue with its link.',
        },

        // Standing on giants: one line on the home page, the roles on /credits
        giants: {
            line: 'StewBeet runs on beet, bolt and mecha, made by the beet team, and fetches the Smithed and Bookshelf libraries your functions call.',
            howItFits: 'How StewBeet fits with beet',
            credits: 'Credits',
            beetRole: 'The pipeline. One build for the datapack and the resource pack.',
            mechaRole: 'The compiler. Type-checked commands, and real Python inside a function.',
            modelResolverRole: 'The renderer. Every item and block drawn to an image, in pure Python.',
            smithedRole: 'The conventions. Crafter, Custom Blocks and Weld, wired up for you.',
            bookshelfRole: 'The toolbox. Call a module in a function and the build fetches it.',
        },

        // Standing on giants: the /credits page
        credits: {
            title: 'Standing on giants',
            subtitle: 'StewBeet did not get here alone. What follows is a thank-you to the projects it is built on, and to the people behind them.',
            beetBody: 'A development kit that unifies datapack and resource pack tooling into a single pipeline. StewBeet is a set of beet plugins, so everything beet knows how to do stays available to you. Built by vberlier (fizzy), misode, edayot (airdox), rx97, TheNuclearNexus, and many more.',
            mechaBody: 'mecha compiles and type-checks every command the build emits, so a typo fails the build instead of the game. bolt lets you script a function in real Python: loops, variables and conditions, compiled down to commands. Both live in the beet repository and carry the same list of names.',
            modelResolverBody: 'Renders every item and block to a real image, in pure Python. That is how the in-game manual shows your crafts without a single screenshot being taken by hand. Thanks @airdox.',
            smithedBody: 'Crafter for NBT recipes and Custom Blocks for placement, both wired up automatically. Smithed also sets shared conventions so packs stay interoperable, even in normal worlds outside the ecosystem. Smithed Weld merges your pack with its dependencies on build.',
            bookshelfBody: 'A modular toolbox of datapack utilities by the Bookshelf team. Call #bs.math:... in a function and StewBeet pulls in just that module, out of the {n} it resolves by name.',
            librariesTitle: 'And the libraries the build fetches for you',
            librariesNote: 'Detected from the functions you write, downloaded at build time, then checked in game with a clickable error message when a version is missing.',
            compatTitle: 'Packs it knows how to get along with',
            compatNote: 'Nothing is downloaded for these. A plugin emits the extra files they look for, so your items show up correctly when a player has them installed.',
            docsLink: 'Read the dependencies guide',
            backHome: 'Back to the home page',
        },

        // The quickstart's commands, at the bottom of the home page
        start: {
            title: 'From nothing to a built pack in two commands',
            needs: 'Needs',
            needsEnd: ', which installs Python 3.14 for you.',
            initText: 'Creates the project. Type basic when it asks for a template.',
            buildText: 'Builds the datapack and the resource pack, zipped in build/.',
            templates: 'basic sets up every plugin with no example to delete, extensive is a full project to read.',
            templatesLink: 'The three templates',
        },

        // Documentation Page
        documentation: {
            title: 'Documentation',
            subtitle: 'Start with the quickstart, then open the guide for the task in front of you. Every plugin has its own page.',
            quickstartDesc: 'Three commands, from nothing to a loadable datapack.',
            gettingStartedDesc: 'Create a project, build it, load it in Minecraft, then add an item and a whole ore tier. About 20 minutes.',
            migrationDesc: 'Turn a datapack or resource pack you already have into a StewBeet project, with a dry run first.',
            editorSupportDesc: 'The VS Code extension: the Bolt language, commands checked inside your Python, and navigation to the built pack.',
            itemsAndBlocksDesc: 'Declare an item and a block, give them a texture and a recipe, and build.',
            writingToFilesDesc: 'Static files, the beet API, StewBeet helpers and Bolt, and when to use each.',
            cookbookDesc: 'Complete, working files you can read top to bottom.',
            dependenciesDesc: 'The libraries the build detects and downloads, and the version checks it writes.',
            ingameManualDesc: 'The generated in-game manual, and its custom pages, hooks and button layouts.',
            continuousDeliveryDesc: 'Publish releases to GitHub, Modrinth, Smithed and PlanetMinecraft in one command.',
            performanceDesc: 'Persistent entities, guarded NBT writes and reused results for code that runs every tick.',
            testingDesc: 'A tests folder run against the built zip on a headless server, and the traps of a pack that waits for a player.',
            postEffectsDesc: 'A /posteffect chain whose shader knows how long it has been applied.',
            simplenergyDesc: "Energy, batteries, cables and machines with SimplEnergy's helpers.",
            definitionsSetupDesc: 'Every field of an Item or a Block, with recipes and equipment tiers.',
            helperReferenceDesc: 'Every helper StewBeet adds for writing files, and what each one takes.',
            beetConfigDesc: 'Every option of beet.yml, the StewBeet ones included.',
            equationsDesc: 'Chainable Equation builders that compile to scoreboard commands.',
            apiDesc: 'Every class and function of the Python package, generated from the code.',
            howItFitsDesc: 'What beet, bolt and mecha do, and where StewBeet plugs in.',
            handledDesc: 'What the build writes and checks so you never do it by hand.',
            pluginsLead: 'Each step of the build is a plugin you can enable, disable or replace.',
            allPlugins: 'Every plugin, in pipeline order',
        },

        // Markdown Page
        markdown: {
            pages: 'Pages',
            onThisPage: 'On this page',
            thisPage: 'This page',
            editOnGithub: 'Edit on GitHub',
            readMarkdown: 'Read as Markdown',
            breadcrumb: 'Breadcrumb',
            filter: 'Filter pages',
            filterPlaceholder: 'recipe, manual, sounds',
            noMatch: 'No page title matches.',
            pluginsCount: '{n} plugins, grouped by what they produce',
            pluginsShort: '{n} plugins',
            previous: 'Previous',
            next: 'Next',
            close: 'Close',
            error: 'This page could not be shown',
            loading: 'Loading the page...',
            noPage: 'No page given. Pick one from the list of pages.',
            notFound: 'There is no page at this address.',
            unreachable: 'The page could not be loaded. Check your connection, then reload.',
        },

        code: {
            terminal: 'Terminal',
        },

        // 404 Page
        notFound: {
            title: 'This page does not exist',
            description: 'The link may be outdated, or the page may have been renamed. The documentation index lists every guide and plugin page.',
            backHome: 'Back to home',
            browseDocs: 'Browse the documentation',
        },

        // Tools Page
        tools: {
            whereEditor: 'VS Code',
            whereBrowser: 'Runs in your browser',
            whereServer: 'Runs on the server',
            title: 'Tools',
            subtitle: 'Things you can use without installing StewBeet, and the extension for when you do.',
            markdownToBBCode: 'Markdown to BBCode Converter',
            markdownToBBCodeDesc: 'Convert Markdown text to BBCode format for publishing on PlanetMinecraft. Supports badges, lists, tables, code blocks, spoilers, and more.',
            playground: 'Playground',
            playgroundDesc: 'Write a definitions module in the browser and see every file StewBeet generates from it, without installing anything.',
            autoHeaders: 'Auto Headers',
            autoHeadersDesc: 'Upload a datapack and get it back with a header on every function: who calls it, the context it runs in and the type of each macro argument. Runs the standalone auto.headers beet plugin.',
            extension: 'VSCode Extension',
            extensionDesc: 'Editor support for the whole beet ecosystem: the Bolt language, plus highlighting, completion, errors and build navigation for the mcfunction strings inside your Python.',
        },

        // Playground
        playground: {
            title: 'Playground',
            subtitle: 'Write a definitions module. Build it. Read every file it produced.',
            presets: 'Start from:',
            // Nested, not 'preset.item': getTranslation splits the key on dots and walks the
            // object, so a literal dotted key can never be reached.
            preset: {
                item: 'An item',
                block: 'A block',
                recipes: 'Recipes',
                render: 'A render in a tooltip',
            },
            build: 'Build',
            building: 'Building...',
            shortcut: 'Ctrl+Enter',
            loadingEditor: 'Loading the editor...',
            output: 'Output',
            filesGenerated: '{count} files generated',
            cached: 'cached',
            viewConfig: 'beet.yml',
            atLine: 'at line {line}:',
            didYouMean: 'Did you mean:',
            fullTraceback: 'Full traceback',
            back: 'Back to the tree',
            empty: 'Press Build to see what this code generates.',
            truncated: 'Showing the first {count} files.',
            limits: 'This runs a reduced StewBeet pipeline. No item renders, no in-game manual, no dependency downloads.',
            limitsDetail: 'Item renders need an OpenGL context, which the build container has no display for, so the in-game manual is off and items get their texture in place of an isometric render. There is no network at all, so dependency resolution and Smithed Weld merging are off, and nothing is archived, hashed or copied anywhere. Only the definitions module runs: no .mcfunction files, no bolt, no mecha, no sounds. Textures come from SimplEnergy, Stardust Fragment and the extensive template; any other item id gets a placeholder and a note in the log.',
            limitsNumbers: 'Each build gets {cpu} seconds of CPU, {wall} seconds of wall clock and {memory} MiB of memory, and returns at most {files} files or {total} MB.',
            fullOutput: 'Run it locally for the whole pipeline',
            error: {
                sandbox_disabled: 'The playground is not available on this deployment.',
                rate_limited: 'Too many builds. Try again in a moment.',
                busy: 'Another build is running. Try again in a few seconds.',
                timeout: 'That build took too long and was stopped.',
                worker_unavailable: 'The build service could not be reached.',
                no_scratch_space: 'The build service is out of scratch space. Try again shortly.',
                code_too_large: 'That code is too large to build.',
                invalid_body: 'There is nothing to build.',
                method_not_allowed: 'That request was not understood.',
                build_failed: 'The build failed. The log is below.',
                crashed: 'The build stopped unexpectedly, usually from running out of memory.',
            },
        },

        // auto.headers
        autoHeaders: {
            title: 'Auto Headers',
            subtitle: 'Upload a datapack. Get it back with a header on every function.',
            pluginLink: 'auto.headers is a standalone beet plugin',
            drop: 'Drop a datapack .zip here, or click to pick one',
            maxSize: 'Up to {size} MB',
            pipeline: 'Pipeline: stewbeet.plugins.auto.headers',
            run: 'Add the headers',
            running: 'Working...',
            output: 'Result',
            rewritten: '{changed} of {functions} functions rewritten',
            download: 'Download ({size})',
            back: 'Back to the tree',
            empty: 'Pick a datapack and press the button to see the headers it gets.',
            fullTraceback: 'Full traceback',
            warningsDropped: 'and {count} more warnings, left out of the response.',
            limits: 'This runs one plugin and nothing else. Your pack comes back as it was, with the function headers rewritten.',
            limitsDetail: 'Only .mcfunction files are touched. Every other file is returned byte for byte as you uploaded it, so a loot table keeps its own formatting and a texture is never re-encoded. The header of each function names its callers, the execution context it runs in and the type of every macro argument, all inferred from the pack itself. Nothing is stored: the archive you download is the only copy, and it never touches a disk on the server.',
            limitsNumbers: 'Uploads are capped at {pack} MB, {extracted} MB once extracted and {entries} files. Each run gets {cpu} seconds of CPU, {wall} seconds of wall clock and {memory} MiB of memory.',
            standalone: 'This page is only a front end. auto.headers is an ordinary beet plugin with no dependency on the rest of StewBeet: put stewbeet.plugins.auto.headers in the pipeline of any beet project and it does the same thing on every build, with a cache that makes an unchanged pack cost nothing.',
            readDocs: 'Read the auto.headers plugin page',
            error: {
                sandbox_disabled: 'This tool is not available on this deployment.',
                rate_limited: 'Too many runs. Try again in a moment.',
                busy: 'Another job is running. Try again in a few seconds.',
                timeout: 'That pack took too long and the run was stopped.',
                worker_unavailable: 'The build service could not be reached.',
                no_scratch_space: 'The build service is out of scratch space. Try again shortly.',
                pack_too_large: 'That archive is too large.',
                pack_too_large_extracted: 'That archive unpacks to more than the sandbox allows.',
                too_many_entries: 'That archive holds more files than the sandbox allows.',
                unsafe_archive: 'That archive contains paths that point outside itself, so it was refused.',
                invalid_archive: 'That file is not a readable .zip archive.',
                no_pack_mcmeta: 'No pack.mcmeta was found in that archive, so it is not a datapack.',
                headers_failed: 'The pass failed on that pack. The traceback is below.',
                crashed: 'The run stopped unexpectedly, usually from running out of memory.',
                invalid_body: 'There is nothing to work on.',
                method_not_allowed: 'That request was not understood.',
            },
        },

        // Search
        search: {
            button: 'Search docs',
            placeholder: 'Search the documentation, plugins and API...',
            hint: 'Type a keyword to search every guide, plugin page and Python symbol.',
            loading: 'Loading the search index...',
            noResults: 'No result found.',
            close: 'Close search',
            hintNavigate: 'to navigate',
            hintOpen: 'to open',
            hintClose: 'to close',
            typeDoc: 'Guide',
            typePlugin: 'Plugin',
            typeApi: 'API',
            typeSite: 'Site',
            sectionDoc: 'Guides',
            sectionApi: 'API',
            sectionPlugin: 'Plugins',
            sectionSite: 'Site',
        },

        // Footer
        footer: {
            tagline: 'A beet framework that turns Python definitions into finished Minecraft datapacks and resource packs.',
            product: 'Product',
            community: 'Community',
            resources: 'Resources',
            vscode: 'VS Code extension',
            credits: 'Credits',
            reportBug: 'Report a bug',
            telemetry: 'Telemetry',
            license: 'MIT licensed',
            by: 'by',
        },

        // Telemetry page
        telemetry: {
            title: 'Telemetry',
            subtitle: 'StewBeet counts successful builds, anonymously, so the project knows whether anyone is using it, and the tools on this site are counted the same way. Here are the numbers, the exact contents of what is sent, and how to switch it off.',

            statsLoading: 'Loading the public numbers...',
            statsUnavailable: 'The public numbers could not be loaded right now.',
            chartAlt: 'Daily counts for the last 30 days.',
            tableToggle: 'Show the numbers as a table',
            tableDate: 'Date (UTC)',
            tableAverage: 'Average',
            noDimensionData: 'Nothing counted yet.',
            streamTabs: 'Which counter to show',
            previousStream: 'Previous counter',
            nextStream: 'Next counter',

            streams: {
                cli: {
                    tab: 'Builds',
                    title: 'Builds over the last 30 days',
                    unit: 'builds',
                    average: 'average build',
                    note: 'Every install of StewBeet that finished a build with telemetry left on. The playground is not in this number: the sandbox runs with STEWBEET_TELEMETRY=0, so what you are looking at is real projects on real machines.',
                    link: '',
                },
                playground: {
                    tab: 'Playground',
                    title: 'Playground runs over the last 30 days',
                    unit: 'runs',
                    average: 'average run',
                    note: 'One count per build the server actually ran. Pressing Build again on code nobody changed is answered from the cache and is not counted a second time, and the code you typed is not part of any of this.',
                    link: 'Open the playground',
                },
                auto_headers: {
                    tab: 'Auto Headers',
                    title: 'Auto Headers runs over the last 30 days',
                    unit: 'packs',
                    average: 'average run',
                    note: 'One count per datapack that was read, with the size band it fell into and how the run ended. The archive is never written to a disk on the server and nothing about its contents is kept.',
                    link: 'Open Auto Headers',
                },
                markdown_to_bbcode: {
                    tab: 'Markdown to BBCode',
                    title: 'Markdown to BBCode conversions over the last 30 days',
                    unit: 'conversions',
                    average: '',
                    note: 'The converter runs entirely in your browser, so this is the one counter the server cannot see for itself: it is a short ping sent when you press Copy or Convert, once the conversion has already happened. Your text never leaves the tab.',
                    link: 'Open the converter',
                },
            },

            dimensions: {
                versions: 'StewBeet versions',
                pythonVersions: 'Python versions',
                durationBuckets: 'Duration',
                outcomes: 'How it ended',
                packSizes: 'Upload size',
                actions: 'What was pressed',
                inputSizes: 'Input size',
            },

            collectedTitle: 'What do we collect?',
            collectedWhy: 'Three fields, sent once a build has finished. The versions say which releases still need supporting, and the duration says whether builds are getting slower between releases.',
            collectedHeading: 'Sent after a successful build',
            collectedVersion: 'The StewBeet version, ex: 3.6.3',
            collectedPython: 'The Python version, ex: 3.14.7',
            collectedDuration: 'How long the build took, in seconds',
            collectedDay: 'The day it arrived, kept as a date and never as a time',

            notCollectedHeading: 'Never sent, never stored',
            notProject: 'Your project, its name or its contents',
            notCode: 'Your source code',
            notPaths: 'Your file paths',
            notUsername: 'Your username',
            notHostname: 'Your hostname',
            notEnv: 'Your environment variables',
            notGit: 'Your repository or its remotes',
            notIp: 'Your IP address, which the server uses to rate limit and then drops',
            notIdentifiers: 'Any installation or user identifier, one-off or persistent',

            aggregateNote: 'The server keeps one row per day per counter: how many events, their total duration, and the distributions that counter declares. Two public endpoints read it back. GET /api/telemetry/builds?days=30 is the build counter, unchanged, and GET /api/telemetry/streams?days=30 is all of them at once.',

            websiteTitle: 'What about the tools on this site?',
            websiteNote: 'The playground and Auto Headers are counted by the server that runs them, which is how the outcome and duration breakdowns exist without your browser sending anything at all. The converter runs in your browser instead, so it sends one short ping when you press Copy or Convert. None of the three records what you uploaded, typed or built, and none of them sets a cookie or an identifier of any kind.',

            disableTitle: 'How can I disable telemetry?',
            disableIntro: 'Set STEWBEET_TELEMETRY=0 before running StewBeet. Nothing is sent, and nothing else about the build changes.',
            disableNote: 'Telemetry is not required for anything: it runs after the build is already finished, on its own thread, with a three second timeout, and a failure is swallowed. An unreachable server can never fail or delay a build.',

            sourceTitle: 'Telemetry implementation',
            sourceIntro: 'The whole client side lives in one file, so you do not have to take any of the above on trust:',
            serverNote: 'The server side is in docs/web/src/api/telemetry/ in the same repository: streams.ts is the list of what gets counted, storage.ts keeps the daily totals, and handlers.ts is the endpoints. Adding a counter is an entry in that list, which is why nothing here is bespoke to one of them.',
            backHome: 'Back to the home page',
        },
    },

    fr: {
        // Navbar
        nav: {
            main: 'Principale',
            menu: 'Menu',
            documentation: 'Docs',
            showcase: 'Showcase',
            playground: 'Playground',
            tools: 'Tools',
            switchLanguage: 'Switch to English',
            themeSystem: 'Thème : celui du système',
            themeLight: 'Thème : clair',
            themeDark: 'Thème : sombre',
        },

        // Hero Section
        hero: {
            releasedDaysAgo: 'publiée il y a {n} jours',
            releasedToday: "publiée aujourd'hui",
            releasedYesterday: 'publiée hier',
            license: 'licence MIT',
            title: 'Des items et blocks custom sans écrire chaque fichier',
            subtitle: "Définissez un item ou un block une fois. StewBeet écrit ses models, recipes, loot tables, traductions et sa page de manuel à chaque build. Les commandes que vous écrivez encore à la main sont vérifiées par Spyglass dans VS Code.",
            readQuickstart: 'Lire le démarrage rapide',
            browseDocs: 'Parcourir la doc',
            newToPython: 'Nouveau en Python ?',
            newToPythonText: "Une définition, c'est un nom, quelques valeurs et une recipe. Si vous savez lire le JSON d'un datapack, vous savez en lire une.",
            proofTitle: 'Un block, défini une fois',
            codeCaption: 'definitions/additions/equipments.py',
            writtenByBuild: 'Écrit par le build :',
            blockFunctions: 'Fonctions du block : {n}',
            crafterRecipes: 'Recipes Smithed Crafter : {n}',
            lootTables: 'Loot tables : {n}',
            manualPages: 'Pages de manuel : {n}',
            resourcePackFiles: 'Fichiers du resource pack : {n}',
            proofCaption: '{n} fichiers à partir de cette seule définition. La première case contient le rendu que le build fait pour le manuel en jeu.',
            replay: 'Rejouer le build',
            ingameCaption: 'En jeu, Minecraft 26.3',
            ingameAlt: 'Le Life Crystal Block posé dans un monde Minecraft',
        },

        // A user quote, beside the objection it answers
        testimonial: {
            casperQuote: "Je ne connaissais pas du tout Python, mais à force d'essais et d'erreurs j'ai fini par comprendre, et c'est génial.",
            casperCaption: 'a fait ses premiers blocks custom avec StewBeet',
            translated: "traduit de l'anglais",
        },

        // The proof that the generated files stay readable, beside the user who feared they would not
        control: {
            title: 'Vous gardez la main sur chaque fichier',
            text: "Le build écrit des fichiers de datapack et de resource pack ordinaires, et note en tête de chaque fonction d'où elle est appelée. Voici les {n} fichiers du block ci-dessus, tels que le build les a écrits.",
            sourceMaps: "Les source maps relient chaque ligne au Python qui l'a écrite.",
            files: 'Fichiers écrits à partir du block',
            racoonQuote: "Avant de l'essayer, j'étais pas mal réfractaire aux précompilateurs, je pensais que toute cette abstraction allait créer du code spaghetti. Mais StewBeet s'intègre tout à fait dans le process de création : il simplifie beaucoup de tâches qui, accumulées, prennent du temps et de la fatigue mentale, tout en gardant un contrôle absolu sur le code qu'on produit.",
            racoonCaption: 'auteur de',
            translated: '',
        },

        // Copy buttons
        copy: {
            action: 'Copier',
            copied: 'Copié',
            command: 'Copier la commande',
        },

        // What one definition saves
        gains: {
            title: 'Un block à la main, c\'est huit fichiers',
            lead: 'Dans deux packs et quatre formats. Oubliez-en un et rien ne plante : le block ne drop jamais. StewBeet écrit les huit depuis la définition à chaque build.',
            byHand: 'À la main',
            withStewbeet: 'Avec StewBeet',
            withUnit: 'définition à maintenir',
            withNote: 'Les huit fichiers en sont écrits à chaque build, donc ils ne divergent jamais.',
            materialsTitle: 'Un matériau, tout le palier',
            materialsText: 'Nommez un lingot et le palier vanilla auquel il correspond. Outils, armures, minerai, block et pépite viennent des textures déposées, recipes comprises.',
            materialsAlt: 'Le lingot de solarium de Stardust Fragment, et les outils, armures et block enregistrés à partir de lui',
            langTitle: 'Votre texte, prêt à traduire',
            langText: 'Écrivez du texte simple dans vos commandes. Le build en fait des clés de traduction et les rassemble dans en_us.json.',
            langBefore: 'Ce que vous écrivez',
            langAfter: 'Ce qu\'écrit le build',
        },

        // In-game manual showcase
        manual: {
            title: 'Votre datapack se documente tout seul',
            description: 'Chaque item défini obtient sa page de manuel : sa recipe dessinée à partir des ingrédients déclarés, sa description, et des liens entre catégories. Les joueurs fabriquent le livre en jeu, et le build suivant le met à jour.',
            readMore: 'Comment fonctionne le manuel',
            videoFallback: 'Votre navigateur ne peut pas lire cette vidéo.',
        },

        // Editor showcase
        editor: {
            title: 'Vos commandes, vérifiées dans votre éditeur',
            description: 'Une commande dans une chaîne Python reste une commande. L\'extension StewBeet pour VS Code lui donne complétion, survol et erreurs pendant la frappe, et Ctrl+clic mène d\'un appel write_function au fichier écrit par le build.',
            install: 'Installer depuis le marketplace',
            readMore: 'Ce qu\'elle fait',
            videoFallback: 'Votre navigateur ne peut pas lire cette vidéo.',
        },

        // Trust strip
        trust: {
            label: 'Activité du projet',
            downloadsPerMonth: 'téléchargements PyPI par mois',
            publicProjects: 'projets publics qui l\'utilisent',
            githubStars: 'étoiles GitHub',
        },

        // Built with StewBeet
        builtWith: {
            title: '{n} projets publics sont faits avec StewBeet',
            subtitle: "Les projets d'autres datapackers d'abord, puis les packs et bibliothèques de l'auteur. Chaque carte ouvre son code source.",
            community: 'communauté',
            previous: 'Projets précédents',
            next: 'Projets suivants',
            filesFrom: '{files} fichiers depuis {lines} lignes de Python',
            seeAll: 'Voir tous les projets.',
        },

        // The /showcase page
        showcase: {
            lead: 'Des datapacks, des jeux et des bibliothèques au code public. Chaque carte ouvre ce code, pour voir comment un vrai projet organise ses définitions.',
            community: 'Par la communauté',
            packs: "Par l'auteur de StewBeet",
            libraries: 'Bibliothèques',
            addTitle: 'Ajoutez le vôtre',
            addText: 'Vous avez fait un projet avec StewBeet et publié son code ?',
            addLink: 'Ouvrez une issue avec son lien.',
        },

        // Standing on giants: one line on the home page, the roles on /credits
        giants: {
            line: 'StewBeet tourne sur beet, bolt et mecha, faits par l\'équipe de beet, et récupère les bibliothèques Smithed et Bookshelf qu\'appellent vos fonctions.',
            howItFits: 'Comment StewBeet s\'intègre à beet',
            credits: 'Crédits',
            beetRole: 'Le pipeline. Un seul build pour le datapack et le resource pack.',
            mechaRole: 'Le compilateur. Des commandes vérifiées, et du vrai Python dans une fonction.',
            modelResolverRole: 'Le rendu. Chaque item et chaque bloc dessinés en image, en Python pur.',
            smithedRole: 'Les conventions. Crafter, Custom Blocks et Weld, branchés pour vous.',
            bookshelfRole: 'La boîte à outils. Appelez un module dans une fonction, le build le récupère.',
        },

        // Standing on giants: the /credits page
        credits: {
            title: 'Sur les épaules de géants',
            subtitle: 'StewBeet n\'est pas arrivé là tout seul. Ce qui suit est un merci aux projets sur lesquels il repose, et aux personnes derrière.',
            beetBody: 'Un kit de développement qui unifie l\'outillage datapack et resource pack dans un seul pipeline. StewBeet est un ensemble de plugins beet : tout ce que beet sait faire reste à votre disposition. Construit par vberlier (fizzy), misode, edayot (airdox), rx97, TheNuclearNexus, et bien d\'autres.',
            mechaBody: 'mecha compile et vérifie le type de chaque commande générée : une faute de frappe casse le build au lieu du jeu. bolt permet d\'écrire une fonction en vrai Python : boucles, variables et conditions, compilées en commandes. Les deux vivent dans le dépôt beet et portent la même liste de noms.',
            modelResolverBody: 'Génère une vraie image de chaque item et de chaque bloc, en Python pur. C\'est comme ça que le manuel en jeu affiche vos crafts sans qu\'une seule capture soit prise à la main. Merci @airdox.',
            smithedBody: 'Crafter pour les recipes NBT et Custom Blocks pour la pose, branchés automatiquement. Smithed pose aussi des conventions communes pour que les packs restent interopérables, même dans un monde normal en dehors de l\'écosystème. Smithed Weld fusionne votre pack avec ses dépendances au build.',
            bookshelfBody: 'Une boîte à outils modulaire d\'utilitaires datapack, par l\'équipe Bookshelf. Appelez #bs.math:... dans une fonction et StewBeet récupère uniquement ce module, parmi les {n} qu\'il sait résoudre par leur nom.',
            librariesTitle: 'Et les bibliothèques que le build récupère pour vous',
            librariesNote: 'Détectées depuis les fonctions que vous écrivez, téléchargées au build, puis vérifiées en jeu avec un message d\'erreur cliquable quand une version manque.',
            compatTitle: 'Les packs avec lesquels il sait s\'entendre',
            compatNote: 'Rien n\'est téléchargé pour ceux-là. Un plugin génère les fichiers supplémentaires qu\'ils cherchent, pour que vos items s\'affichent correctement chez un joueur qui les a installés.',
            docsLink: 'Lire le guide des dépendances',
            backHome: 'Retour à l\'accueil',
        },

        // The quickstart's commands, at the bottom of the home page
        start: {
            title: 'De rien à un pack compilé en deux commandes',
            needs: 'Il faut',
            needsEnd: ', qui installe Python 3.14 pour vous.',
            initText: 'Crée le projet. Tapez basic quand il demande un template.',
            buildText: 'Compile le datapack et le resource pack, zippés dans build/.',
            templates: 'basic configure chaque plugin sans exemple à supprimer, extensive est un projet complet à lire.',
            templatesLink: 'Les trois templates',
        },

        // Documentation Page
        documentation: {
            title: 'Documentation',
            subtitle: 'Commencez par le quickstart, puis ouvrez le guide de la tâche du moment. Chaque plugin a sa propre page.',
            quickstartDesc: 'Trois commandes, de rien à un datapack chargeable.',
            gettingStartedDesc: 'Créez un projet, compilez-le, chargez-le dans Minecraft, puis ajoutez un item et tout un palier de minerai. Environ 20 minutes.',
            migrationDesc: "Transformez un datapack ou un resource pack que vous avez déjà en projet StewBeet, avec un essai à blanc d'abord.",
            editorSupportDesc: "L'extension VS Code : le langage Bolt, les commandes vérifiées dans votre Python, et la navigation vers le pack construit.",
            itemsAndBlocksDesc: 'Déclarez un item et un block, donnez-leur une texture et une recipe, et compilez.',
            writingToFilesDesc: 'Fichiers statiques, API beet, helpers StewBeet et Bolt, et quand utiliser chacun.',
            cookbookDesc: 'Des fichiers complets et fonctionnels, à lire de bout en bout.',
            dependenciesDesc: 'Les bibliothèques que le build détecte et télécharge, et les vérifications de version qu\'il écrit.',
            ingameManualDesc: 'Le manuel en jeu généré, avec ses custom pages, hooks et agencements de boutons.',
            continuousDeliveryDesc: 'Publiez des releases sur GitHub, Modrinth, Smithed et PlanetMinecraft en une seule commande.',
            performanceDesc: 'Entités persistantes, écritures NBT conditionnelles et résultats réutilisés pour le code exécuté à chaque tick.',
            testingDesc: "Un dossier de tests lancé sur le zip construit dans un serveur sans interface, et les pièges d'un pack qui attend un joueur.",
            postEffectsDesc: 'Une chaîne /posteffect dont le shader sait depuis combien de temps elle est appliquée.',
            simplenergyDesc: 'Énergie, batteries, câbles et machines avec les helpers de SimplEnergy.',
            definitionsSetupDesc: "Chaque champ d'un Item ou d'un Block, avec les recipes et les paliers d'équipement.",
            helperReferenceDesc: 'Chaque helper que StewBeet ajoute pour écrire des fichiers, et ses arguments.',
            beetConfigDesc: 'Chaque option de beet.yml, celles de StewBeet comprises.',
            equationsDesc: 'Des constructeurs Equation chaînables qui compilent en commandes scoreboard.',
            apiDesc: 'Chaque classe et fonction du package Python, générées depuis le code.',
            howItFitsDesc: 'Ce que font beet, bolt et mecha, et où StewBeet se branche.',
            handledDesc: 'Ce que le build écrit et vérifie pour que vous ne le fassiez jamais à la main.',
            pluginsLead: 'Chaque étape du build est un plugin que vous pouvez activer, désactiver ou remplacer.',
            allPlugins: "Tous les plugins, dans l'ordre du pipeline",
        },

        // Markdown Page
        markdown: {
            pages: 'Pages',
            onThisPage: 'Sur cette page',
            thisPage: 'Cette page',
            editOnGithub: 'Modifier sur GitHub',
            readMarkdown: 'Lire en Markdown',
            breadcrumb: "Fil d'Ariane",
            filter: 'Filtrer les pages',
            filterPlaceholder: 'recipe, manuel, sons',
            noMatch: 'Aucun titre de page ne correspond.',
            pluginsCount: "{n} plugins, rangés par ce qu'ils produisent",
            pluginsShort: '{n} plugins',
            previous: 'Précédent',
            next: 'Suivant',
            close: 'Fermer',
            error: "Cette page n'a pas pu s'afficher",
            loading: 'Chargement de la page...',
            noPage: 'Aucune page demandée. Choisissez-en une dans la liste des pages.',
            notFound: "Il n'y a pas de page à cette adresse.",
            unreachable: "La page n'a pas pu être chargée. Vérifiez votre connexion, puis rechargez.",
        },

        code: {
            terminal: 'Terminal',
        },

        // 404 Page
        notFound: {
            title: "Cette page n'existe pas",
            description: "Le lien est peut-être obsolète, ou la page a été renommée. L'index de la documentation liste tous les guides et toutes les pages de plugins.",
            backHome: "Retour à l'accueil",
            browseDocs: 'Parcourir la documentation',
        },

        // Tools Page
        tools: {
            whereEditor: 'VS Code',
            whereBrowser: 'Tourne dans votre navigateur',
            whereServer: 'Tourne sur le serveur',
            title: 'Outils',
            subtitle: 'Ce que vous pouvez utiliser sans installer StewBeet, et l\'extension pour quand vous l\'aurez.',
            markdownToBBCode: 'Convertisseur Markdown vers BBCode',
            markdownToBBCodeDesc: 'Convertissez du texte Markdown en format BBCode pour publier sur PlanetMinecraft. Supporte les badges, listes, tableaux, blocs de code, spoilers et plus.',
            playground: 'Playground',
            playgroundDesc: 'Écrivez un module de definitions dans le navigateur et voyez tous les fichiers que StewBeet en génère, sans rien installer.',
            autoHeaders: 'Auto Headers',
            autoHeadersDesc: 'Envoyez un datapack et récupérez-le avec un header sur chaque function : qui l\'appelle, le contexte dans lequel elle s\'exécute et le type de chaque argument de macro. Exécute le plugin beet indépendant auto.headers.',
            extension: 'Extension VSCode',
            extensionDesc: 'Le support éditeur de tout l\'écosystème beet : le langage Bolt, plus la coloration, la complétion, les erreurs et la navigation vers le build pour les chaînes mcfunction dans votre Python.',
        },

        // Playground
        playground: {
            title: 'Playground',
            subtitle: 'Écrivez un module de definitions. Compilez. Lisez chaque fichier produit.',
            presets: 'Partir de :',
            preset: {
                item: 'Un item',
                block: 'Un block',
                recipes: 'Des recipes',
                render: 'Un render dans un tooltip',
            },
            build: 'Compiler',
            building: 'Compilation...',
            shortcut: 'Ctrl+Entrée',
            loadingEditor: 'Chargement de l\'éditeur...',
            output: 'Résultat',
            filesGenerated: '{count} fichiers générés',
            cached: 'en cache',
            viewConfig: 'beet.yml',
            atLine: 'à la ligne {line} :',
            didYouMean: 'Vouliez-vous dire :',
            fullTraceback: 'Traceback complet',
            back: 'Retour à l\'arborescence',
            empty: 'Cliquez sur Compiler pour voir ce que ce code génère.',
            truncated: 'Affichage des {count} premiers fichiers.',
            limits: 'Ceci exécute un pipeline StewBeet réduit. Pas de renders d\'items, pas de manual in-game, pas de téléchargement de dependencies.',
            limitsDetail: 'Les renders d\'items nécessitent un contexte OpenGL, or le conteneur de build n\'a aucun affichage : le manual in-game est donc désactivé et chaque item reçoit sa texture au lieu d\'un render isométrique. Il n\'y a aucun réseau, donc la résolution des dependencies et la fusion Smithed Weld sont désactivées, et rien n\'est archivé, hashé ni copié. Seul le module de definitions est exécuté : pas de fichiers .mcfunction, pas de bolt, pas de mecha, pas de sons. Les textures viennent de SimplEnergy, Stardust Fragment et du template extensive ; tout autre id d\'item reçoit un placeholder et une note dans le log.',
            limitsNumbers: 'Chaque build dispose de {cpu} secondes de CPU, {wall} secondes de temps réel et {memory} Mio de mémoire, et renvoie au plus {files} fichiers ou {total} Mo.',
            fullOutput: 'Lancez-le en local pour le pipeline complet',
            error: {
                sandbox_disabled: 'Le playground n\'est pas disponible sur ce déploiement.',
                rate_limited: 'Trop de builds. Réessayez dans un instant.',
                busy: 'Un autre build est en cours. Réessayez dans quelques secondes.',
                timeout: 'Ce build a pris trop de temps et a été arrêté.',
                worker_unavailable: 'Le service de build est injoignable.',
                no_scratch_space: 'Le service de build n\'a plus d\'espace temporaire. Réessayez bientôt.',
                code_too_large: 'Ce code est trop volumineux pour être compilé.',
                invalid_body: 'Il n\'y a rien à compiler.',
                method_not_allowed: 'Cette requête n\'a pas été comprise.',
                build_failed: 'Le build a échoué. Le log est ci-dessous.',
                crashed: 'Le build s\'est arrêté brutalement, généralement par manque de mémoire.',
            },
        },

        // auto.headers
        autoHeaders: {
            title: 'Auto Headers',
            subtitle: 'Envoyez un datapack. Récupérez-le avec un header sur chaque function.',
            pluginLink: 'auto.headers est un plugin beet indépendant',
            drop: 'Déposez un .zip de datapack ici, ou cliquez pour en choisir un',
            maxSize: 'Jusqu\'à {size} Mo',
            pipeline: 'Pipeline : stewbeet.plugins.auto.headers',
            run: 'Ajouter les headers',
            running: 'Traitement...',
            output: 'Résultat',
            rewritten: '{changed} functions réécrites sur {functions}',
            download: 'Télécharger ({size})',
            back: 'Retour à l\'arborescence',
            empty: 'Choisissez un datapack et cliquez sur le bouton pour voir les headers obtenus.',
            fullTraceback: 'Traceback complet',
            warningsDropped: 'et {count} autres avertissements, non inclus dans la réponse.',
            limits: 'Ceci exécute un seul plugin. Votre pack revient tel quel, avec les headers de functions réécrits.',
            limitsDetail: 'Seuls les fichiers .mcfunction sont touchés. Tous les autres reviennent octet pour octet tels que vous les avez envoyés : une loot table garde son propre formatage et une texture n\'est jamais réencodée. Le header de chaque function nomme ses appelants, le contexte d\'exécution dans lequel elle tourne et le type de chaque argument de macro, le tout déduit du pack lui-même. Rien n\'est conservé : l\'archive que vous téléchargez est la seule copie, et elle ne touche jamais un disque côté serveur.',
            limitsNumbers: 'Les envois sont limités à {pack} Mo, {extracted} Mo une fois décompressés et {entries} fichiers. Chaque exécution dispose de {cpu} secondes de CPU, {wall} secondes de temps réel et {memory} Mio de mémoire.',
            standalone: 'Cette page n\'est qu\'une interface. auto.headers est un plugin beet ordinaire, sans dépendance au reste de StewBeet : mettez stewbeet.plugins.auto.headers dans le pipeline de n\'importe quel projet beet et il fait la même chose à chaque build, avec un cache qui rend un pack inchangé gratuit.',
            readDocs: 'Voir la page du plugin auto.headers',
            error: {
                sandbox_disabled: 'Cet outil n\'est pas disponible sur ce déploiement.',
                rate_limited: 'Trop d\'exécutions. Réessayez dans un instant.',
                busy: 'Une autre tâche est en cours. Réessayez dans quelques secondes.',
                timeout: 'Ce pack a pris trop de temps et l\'exécution a été arrêtée.',
                worker_unavailable: 'Le service de build est injoignable.',
                no_scratch_space: 'Le service de build n\'a plus d\'espace temporaire. Réessayez bientôt.',
                pack_too_large: 'Cette archive est trop volumineuse.',
                pack_too_large_extracted: 'Cette archive décompressée dépasse ce que le sandbox autorise.',
                too_many_entries: 'Cette archive contient plus de fichiers que le sandbox n\'autorise.',
                unsafe_archive: 'Cette archive contient des chemins qui pointent en dehors d\'elle-même, elle a été refusée.',
                invalid_archive: 'Ce fichier n\'est pas une archive .zip lisible.',
                no_pack_mcmeta: 'Aucun pack.mcmeta trouvé dans cette archive, ce n\'est donc pas un datapack.',
                headers_failed: 'Le traitement a échoué sur ce pack. Le traceback est ci-dessous.',
                crashed: 'L\'exécution s\'est arrêtée brutalement, généralement par manque de mémoire.',
                invalid_body: 'Il n\'y a rien à traiter.',
                method_not_allowed: 'Cette requête n\'a pas été comprise.',
            },
        },

        // Search
        search: {
            button: 'Rechercher',
            placeholder: 'Rechercher dans la documentation, les plugins et l\'API...',
            hint: 'Tapez un mot-clé pour chercher dans chaque guide, page de plugin et symbole Python.',
            loading: 'Chargement de l\'index de recherche...',
            noResults: 'Aucun résultat trouvé.',
            close: 'Fermer la recherche',
            hintNavigate: 'pour naviguer',
            hintOpen: 'pour ouvrir',
            hintClose: 'pour fermer',
            typeDoc: 'Guide',
            typePlugin: 'Plugin',
            typeApi: 'API',
            typeSite: 'Site',
            sectionDoc: 'Guides',
            sectionApi: 'API',
            sectionPlugin: 'Plugins',
            sectionSite: 'Site',
        },

        // Footer
        footer: {
            tagline: 'Un framework beet qui transforme des définitions Python en datapacks et resource packs finis.',
            product: 'Produit',
            community: 'Communauté',
            resources: 'Ressources',
            vscode: 'Extension VS Code',
            credits: 'Remerciements',
            reportBug: 'Signaler un bug',
            telemetry: 'Télémétrie',
            license: 'Licence MIT',
            by: 'par',
        },

        // Telemetry page
        telemetry: {
            title: 'Télémétrie',
            subtitle: "StewBeet compte les builds réussis, de façon anonyme, pour savoir si le projet sert à quelqu'un, et les outils de ce site sont comptés de la même manière. Voici les chiffres, le contenu exact de ce qui est envoyé, et comment le désactiver.",

            statsLoading: 'Chargement des chiffres publics...',
            statsUnavailable: "Les chiffres publics n'ont pas pu être chargés pour le moment.",
            chartAlt: 'Comptage par jour sur les 30 derniers jours.',
            tableToggle: 'Afficher les chiffres sous forme de tableau',
            tableDate: 'Date (UTC)',
            tableAverage: 'Moyenne',
            noDimensionData: 'Rien de compté pour le moment.',
            streamTabs: 'Quel compteur afficher',
            previousStream: 'Compteur précédent',
            nextStream: 'Compteur suivant',

            streams: {
                cli: {
                    tab: 'Builds',
                    title: 'Builds sur les 30 derniers jours',
                    unit: 'builds',
                    average: 'build moyen',
                    note: "Chaque installation de StewBeet ayant terminé un build avec la télémétrie activée. Le playground n'entre pas dans ce chiffre : le bac à sable tourne avec STEWBEET_TELEMETRY=0, donc ce sont de vrais projets sur de vraies machines.",
                    link: '',
                },
                playground: {
                    tab: 'Playground',
                    title: 'Exécutions du playground sur les 30 derniers jours',
                    unit: 'exécutions',
                    average: 'exécution moyenne',
                    note: "Un comptage par build réellement exécuté par le serveur. Relancer un build sur du code inchangé est servi depuis le cache et n'est pas compté une deuxième fois, et le code que vous avez tapé n'entre dans rien de tout ça.",
                    link: 'Ouvrir le playground',
                },
                auto_headers: {
                    tab: 'Auto Headers',
                    title: 'Exécutions de Auto Headers sur les 30 derniers jours',
                    unit: 'packs',
                    average: 'exécution moyenne',
                    note: "Un comptage par datapack lu, avec sa tranche de taille et la façon dont l'exécution s'est terminée. L'archive n'est jamais écrite sur un disque du serveur et rien de son contenu n'est conservé.",
                    link: 'Ouvrir Auto Headers',
                },
                markdown_to_bbcode: {
                    tab: 'Markdown vers BBCode',
                    title: 'Conversions Markdown vers BBCode sur les 30 derniers jours',
                    unit: 'conversions',
                    average: '',
                    note: "Le convertisseur tourne entièrement dans votre navigateur : c'est le seul compteur que le serveur ne peut pas voir de lui-même. Un court ping part quand vous cliquez sur Copier ou Convertir, une fois la conversion déjà faite. Votre texte ne quitte jamais l'onglet.",
                    link: 'Ouvrir le convertisseur',
                },
            },

            dimensions: {
                versions: 'Versions de StewBeet',
                pythonVersions: 'Versions de Python',
                durationBuckets: 'Durée',
                outcomes: "Fin de l'exécution",
                packSizes: 'Taille envoyée',
                actions: 'Bouton utilisé',
                inputSizes: "Taille de l'entrée",
            },

            collectedTitle: 'Que collectons-nous ?',
            collectedWhy: "Trois champs, envoyés une fois le build terminé. Les versions indiquent lesquelles méritent encore d'être supportées, et la durée indique si les builds ralentissent de version en version.",
            collectedHeading: 'Envoyé après un build réussi',
            collectedVersion: 'La version de StewBeet, ex : 3.6.3',
            collectedPython: 'La version de Python, ex : 3.14.7',
            collectedDuration: 'La durée du build, en secondes',
            collectedDay: "Le jour d'arrivée, gardé comme une date et jamais comme une heure",

            notCollectedHeading: 'Jamais envoyé, jamais stocké',
            notProject: 'Votre projet, son nom ou son contenu',
            notCode: 'Votre code source',
            notPaths: 'Vos chemins de fichiers',
            notUsername: "Votre nom d'utilisateur",
            notHostname: 'Le nom de votre machine',
            notEnv: "Vos variables d'environnement",
            notGit: 'Votre dépôt ou ses remotes',
            notIp: 'Votre adresse IP, que le serveur utilise pour limiter le débit puis oublie',
            notIdentifiers: "Le moindre identifiant d'installation ou d'utilisateur, temporaire ou permanent",

            aggregateNote: "Le serveur garde une ligne par jour et par compteur : le nombre d'événements, leur durée totale et les répartitions que ce compteur déclare. Deux points d'accès publics les relisent. GET /api/telemetry/builds?days=30 reste le compteur de builds, inchangé, et GET /api/telemetry/streams?days=30 les renvoie tous d'un coup.",

            websiteTitle: 'Et les outils de ce site ?',
            websiteNote: "Le playground et Auto Headers sont comptés par le serveur qui les exécute, ce qui permet d'avoir les répartitions de fin d'exécution et de durée sans que votre navigateur n'envoie quoi que ce soit. Le convertisseur, lui, tourne dans votre navigateur : il envoie un court ping quand vous cliquez sur Copier ou Convertir. Aucun des trois n'enregistre ce que vous avez envoyé, tapé ou construit, et aucun ne pose de cookie ni d'identifiant.",

            disableTitle: 'Comment désactiver la télémétrie ?',
            disableIntro: "Définissez STEWBEET_TELEMETRY=0 avant de lancer StewBeet. Rien n'est envoyé, et rien d'autre ne change dans le build.",
            disableNote: "La télémétrie n'est nécessaire à rien : elle tourne une fois le build déjà terminé, sur son propre thread, avec un délai de trois secondes, et toute erreur est ignorée. Un serveur injoignable ne peut ni faire échouer ni ralentir un build.",

            sourceTitle: 'Le code de la télémétrie',
            sourceIntro: "Toute la partie cliente tient dans un seul fichier, pour que vous n'ayez rien à croire sur parole :",
            serverNote: "La partie serveur se trouve dans docs/web/src/api/telemetry/ du même dépôt : streams.ts est la liste de ce qui est compté, storage.ts garde les totaux journaliers, handlers.ts contient les points d'accès. Ajouter un compteur, c'est une entrée dans cette liste, et c'est pour ça que rien ici n'est écrit sur mesure pour l'un d'eux.",
            backHome: "Retour à l'accueil",
        },
    },
} as const;

export type TranslationKeys = typeof translations.en;
export type NestedKeyOf<T> = T extends object
    ? {
          [K in keyof T]: K extends string
              ? T[K] extends object
                  ? `${K}.${NestedKeyOf<T[K]>}`
                  : K
              : never;
      }[keyof T]
    : never;

export function getTranslation(lang: Language, key: string): string {
    const keys = key.split('.');
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    let value: any = translations[lang];

    for (const k of keys) {
        value = value?.[k];
        if (value === undefined) {
            console.warn(`Translation key not found: ${key} for language: ${lang}`);
            return key;
        }
    }

    return value;
}
