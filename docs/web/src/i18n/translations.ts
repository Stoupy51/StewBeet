import type { Language } from '../context/LanguageContext';

export const translations = {
    en: {
        // Navbar
        nav: {
            features: 'Features',
            installation: 'Installation',
            templates: 'Templates',
            plugins: 'Plugins',
            documentation: 'Documentation',
            tools: 'Tools',
            github: 'GitHub',
            language: 'Language',
        },

        // Hero Section
        hero: {
            versionStable: 'Stable Release',
            titleLine1: 'Define a block in Python.',
            titleLine2: 'Get the whole datapack.',
            description: 'StewBeet is a',
            beet: 'Beet',
            descriptionContinued: 'framework for Minecraft datapacks. Describe your content once. Models, recipes, loot tables, translations and an in-game manual are all built from it on every compile.',
            getStarted: 'Get Started',
            viewDocs: 'Documentation',
            codeCaption: 'definitions/additions/equipments.py',
            outputCaption: 'build/',
            outputSummary: '15 files generated',
            outputNote: 'Placement, destruction, the Silk Touch branch, the recipe and its drawn crafting grid, world generation, models and textures. The manual page and the translation keys come with it.',
        },

        // In-game manual showcase
        manual: {
            title: 'Your datapack documents itself',
            description: 'Every item you define gets a manual page: its recipe drawn from the ingredients you declared, its description, and clickable navigation between categories. Players craft the book in-game and it is already up to date.',
            point1: 'Recipes rendered from your definitions, not screenshotted by hand',
            point2: 'New item today, new manual page on the next build',
            point3: 'Custom pages, hooks and button layouts when you need them',
            readMore: 'How the manual works',
            videoFallback: 'Your browser cannot play this video.',
        },

        // Features
        features: {
            title: 'What you stop writing',
            subtitle: 'Six things StewBeet generates from definitions you already wrote.',

            recipesTitle: 'Recipes reach every crafting system at once',
            recipesDesc: 'Declare a recipe on the item. The vanilla recipe, the Smithed Crafter NBT recipe and the furnace variant all come out of that single declaration.',

            itemModelsTitle: 'Textures become models without touching JSON',
            itemModelsDesc: 'Drop top, side and bottom PNGs into assets/textures and the block is recognised as a cube. An _on suffix gives you the powered state for free.',

            materialsTitle: 'One material, the whole tier',
            materialsDesc: 'Name an ingot and what it is equivalent to. Tools, armour, ore, blocks and nuggets are registered from the textures you dropped in, recipes included.',

            lootTablesTitle: 'Every item is givable, immediately',
            lootTablesDesc: 'Each defined item gets a loot table, plus a _give_all function that hands you the entire pack in named chests for testing.',

            langTitle: 'Translation keys extracted from your code',
            langDesc: 'Write your text once in Python. en_us.json is generated from what you actually wrote, so the lang file never drifts from the items.',

            dependenciesTitle: 'A missing library tells the player what to download',
            materialsImageAlt: 'One ingot texture, and the tools and armour registered from it',
            materialsSnippetLabel: 'the whole tier from one entry',
            itemModelsOnLabel: 'electric_furnace_on.json (written because a _front_on texture exists)',
            recipesSnippetLabel: 'generated, NBT-aware',
            langBeforeLabel: 'what you wrote',
            langAfterLabel: 'what is built, the text became a translate key',
            langFileLabel: 'and the keys it collected',
            dependenciesDesc: 'StewBeet reads your functions, works out which libraries you actually used, fetches them and writes the runtime version check. Load without one and the chat names it, with a clickable link.',
        },

        // Trust strip
        trust: {
            label: 'Project activity',
            releasedDaysAgo: 'released {n} days ago',
            latestRelease: 'latest release',
            downloadsPerMonth: 'PyPI downloads / month',
            publicProjects: 'public projects built with it',
            githubStars: 'GitHub stars',
        },

        // Why StewBeet exists
        why: {
            title: 'Why this exists',
            intro: 'A datapack is not one file per feature. Adding a single custom block means writing its loot table, its item definition, its model, its recipe in every crafting system you support, its translation key, and its placement and destruction functions, by hand, in seven directories, in four formats.',
            pain1: 'Miss one of those files and nothing errors. The block just quietly does not drop, or does not craft, and you find out in-game twenty minutes later.',
            pain2: 'Rename an item and you are doing find-and-replace across hundreds of JSON files, hoping nothing shared that string.',
            pain3: 'The same recipe has to be written once as vanilla JSON and again for every NBT crafting system you support, in a different format each time. Change the ingredients and you change it everywhere, or it silently disagrees with itself.',
            resolution: 'StewBeet makes one definition the only thing you maintain. Every file above is derived from it on each build, so they cannot drift apart. Change the ingredients once and the vanilla recipe, the Smithed Crafter recipe and the furnace variant all follow.',
            noPython: 'You do not need to know Python to use it. A definition is a name, some values and a list of recipes, closer to filling in a form than to writing a program. If you can read a datapack JSON file, you can read one of these.',
            byHandTitle: 'One custom block, by hand',
            byHandNote: 'Eight files across two packs and four formats, for one block. Miss one and nothing errors.',
            limitsTitle: 'Where it will not help you',
            limitsBody: 'It is opinionated. The project layout, the Smithed conventions and the build pipeline are decisions the framework has already made, and working against them is harder than working without it. It needs Python 3.14+ installed on your machine. And if your pack is a handful of functions, writing them by hand is genuinely the right call.',
        },

        // Built with StewBeet
        builtWith: {
            title: 'Built with StewBeet',
            subtitle: 'Public source you can read, compiled with the framework.',
            community: 'Written by other people',
            communityNote: 'Not maintained by the framework author',
            atScale: 'What it handles at scale',
            atScaleNote: "The author's own packs, counted from their build output",
            maintainerPacks: 'Also by the author',
            libraries: 'Libraries & tools',
            integrations: 'Works with the libraries you already use',
            integrationsNote: 'Detected from your code and merged into the build automatically.',
            seeAll: 'See the full list on GitHub',
            unitSourceLines: 'lines of Python (no comments) produce',
            itemsAlt: 'Every item in {project}, drawn from its build',
            sourceLink: 'source',
            showCount: 'show {n}',
            hide: 'hide',
            unitFunctions: '.mcfunction',
            unitJson: '.json',
            unitTextures: 'textures',
            stardustDesc: 'A large progression pack: custom ore tiers, blocks, paintings and a full in-game manual.',
            simplenergyDesc: 'An energy and machine library other packs depend on, with cables, generators and machines.',
        },

        // Final call to action
        finalCta: {
            title: 'Define a block. Build the pack.',
            subtitle: 'The Basic template wires up every plugin with commented configuration and no example content to delete.',
            action: 'Read the getting started guide',
            microcopy: 'MIT licensed · Python 3.14+ · no account needed',
            copyCommand: 'Copy the install command',
            copied: 'Install command copied',
        },

        // Installation
        installation: {
            title: 'From nothing to a built pack in',
            titleHighlight: 'four commands',
            step1: 'Install Python',
            step1Desc: 'StewBeet needs Python 3.14 or newer',
            step2: 'Install StewBeet',
            step2Desc: 'One pip install, dependencies included',
            step3: 'Initialize Project',
            step3Desc: 'Pick a template, get a working project',
            step4: 'Build',
            step4Desc: 'Datapack and resource pack, zipped',
        },

        // Templates
        templates: {
            title: 'Start from a template',
            subtitle: 'Three starting points. The',
            subtitleHighlight: 'Basic',
            subtitleEnd: 'template is the one to pick if you are unsure.',
            minimal: 'Minimal',
            minimalDesc: 'One stewbeet plugin and nothing else, so you can see what beet does on its own.',
            minimalBestFor: 'Learning Beet basics',
            basic: 'Basic',
            basicDesc: 'Every plugin configured and commented, with no example content to delete afterwards.',
            basicBestFor: 'Most users (recommended)',
            extensive: 'Extensive',
            extensiveDesc: 'A working project using every feature: ore tiers, custom blocks, paintings, a manual.',
            extensiveBestFor: 'Reading real examples',
            recommended: 'Recommended',
            downloadZip: 'or download .zip',
            tipTitle: 'Which one?',
            tipBody: 'Take the Basic template. It wires up every plugin with commented configuration and no example content, so you add only what your project needs.',
        },

        // Showcase / plugins listing
        showcase: {
            subtitle: 'Each step of the build is a plugin you can enable, disable or replace.',
            legend: 'Legend:',
            fullyDependent: 'Fully dependent',
            partlyDependent: 'Partly dependent',
            independent: 'Independent',
        },

        // Plugins Table
        pluginsTable: {
            category: 'Category',
            plugin: 'Plugin',
            description: 'Description',
            image: 'Image',
            dependency: 'Dependency',
            // Categories
            categoryCore: 'Core',
            categoryResourcePack: 'Resource Pack',
            categoryRecipes: 'Recipes',
            categoryCustomContent: 'Custom Content',
            categoryDocumentation: 'Documentation',
            categoryDatapack: 'Datapack',
            categoryFinalization: 'Finalization',
            categoryAutomation: 'Automation',
            categoryBuild: 'Build',
            categoryCompatibility: 'Compatibility',
            // Plugins
            initializeDesc: 'Initializes the framework and sets up project metadata',
            verifyDefinitionsDesc: 'Validates the structure of definitions and checks consistency',
            soundsDesc: 'Processes sound files and generates sounds.json automatically',
            itemModelsDesc: 'Automatically generates item and block models',
            checkPowerOf2Desc: 'Validates that textures use power-of-2 resolutions',
            customRecipesDesc: 'Generates vanilla, smithed, furnace, and pulverizer recipes',
            customPaintingsDesc: 'Creates custom painting variants',
            ingameManualDesc: 'Generates an interactive in-game manual with documentation',
            loadingDesc: 'Sets up the loading system with versioning',
            customBlocksDesc: 'Implements placement, destruction, and interaction for custom blocks',
            lootTablesDesc: 'Generates loot tables and give-all functionality',
            sortersDesc: 'Generates sorting functions for NBT lists',
            simpledrawerDesc: 'Adds SimpleDrawer material compatibility for compacted drawers',
            neoEnchantDesc: 'Provides NeoEnchant veinminer compatibility for custom ores',
            customBlocksTickingDesc: 'Configures the ticking system for custom blocks',
            basicDatapackStructureDesc: 'Creates the timing structure (tick, second, minute)',
            dependenciesDesc: 'Manages external library dependencies',
            checkUnusedTexturesDesc: 'Identifies unused textures in the resource pack',
            langFileDesc: 'Automatically generates language files',
            headersDesc: 'Adds automatic headers to mcfunction files',
            scoreboardConstantsDesc: 'Detects scoreboard constant usages and generates initialization commands',
            archiveDesc: 'Creates zip archives of datapacks and resource packs',
            mergeSmithedWeldDesc: 'Merges datapacks and resource packs with libraries',
            copyToDestinationDesc: 'Copies generated packs to destination folders',
            livereloadDesc: 'Auto in-game /reload on each build via link or copy destinations',
            computeSha1Desc: 'Computes SHA1 hashes for all zip files',
        },

        // Documentation Page
        documentation: {
            title: 'Documentation',
            subtitle: 'Learn how to use StewBeet',
            cookbook: 'Cookbook',
            cookbookDesc: 'Complete, working files you can read top to bottom.',
            helperReference: 'Helper function reference',
            helperReferenceDesc: 'Every helper StewBeet adds for writing files, and what each one takes.',
            quickstart: 'Quickstart',
            quickstartDesc: 'Three commands, from nothing to a loadable datapack. Verified end to end.',
            gettingStarted: 'Tutorial: build your first datapack',
            groupStart: 'Start here',
            groupStartDesc: 'Install the framework and build a working pack end to end.',
            groupGuides: 'Guides',
            groupGuidesDesc: 'One task each, in roughly the order you meet them.',
            groupReference: 'Reference',
            groupReferenceDesc: 'Look-up material: APIs, options and generated output.',
            gettingStartedDesc: 'Complete guide for beginners - installation, setup, and creating your first datapack',
            definitionsSetup: 'Defining items and blocks',
            definitionsSetupDesc: 'Learn how to define custom items, blocks, and equipment configurations',
            writingToFiles: 'Writing functions and files',
            writingToFilesDesc: 'Master file writing with static loading, native beet API, and StewBeet helper functions',
            beetConfig: 'Configuring the build',
            beetConfigDesc: 'Complete reference for all beet.yml configuration options including StewBeet-specific settings',
            equations: 'Equations',
            equationsDesc: 'Chainable Equation builders that compile to Minecraft scoreboard commands',
            dependencies: 'Using datapack libraries',
            dependenciesDesc: 'Declare library dependencies and auto-generate runtime version checks',
            continuousDelivery: 'Shipping releases automatically',
            continuousDeliveryDesc: 'Publish releases to GitHub, Modrinth, Smithed, and PlanetMinecraft in one command',
            ingameManual: 'Generating the in-game manual',
            ingameManualDesc: 'Generate an extensible, dialog-first in-game manual with custom pages, hooks, and button layouts',
            plugins: 'Available Plugins',
            comingSoon: 'More guides are being written.',
            searchPlaceholder: 'Search plugins...',
            filterAll: 'All',
            filterCore: 'Core',
            filterCompatibility: 'Compatibility',
            filterDatapack: 'Datapack',
            pluginName: 'Plugin',
            description: 'Description',
            noResults: 'No plugins found matching your search.',
        },

        // Markdown Page
        markdown: {
            back: 'Back',
            contents: 'Contents',
            viewOnGithub: 'View on GitHub',
            error: 'Error',
            loading: 'Loading...',
            noPlugin: 'No plugin specified. Please provide a "src" parameter.',
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
            title: 'Tools',
            subtitle: 'Useful tools for StewBeet and Minecraft datapack development',
            markdownToBBCode: 'Markdown to BBCode Converter',
            markdownToBBCodeDesc: 'Convert Markdown text to BBCode format for publishing on PlanetMinecraft. Supports badges, lists, tables, code blocks, spoilers, and more.',
        },

        // Search
        search: {
            button: 'Search',
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
            tagline: 'A Beet framework that turns Python definitions into finished Minecraft datapacks and resource packs.',
            community: 'Community',
            resources: 'Resources',
            github: 'GitHub',
            discord: 'Discord',
            youtube: 'YouTube',
            pypiPackage: 'PyPI Package',
            planetMinecraft: 'PlanetMinecraft',
            reportBug: 'Report Bug',
            license: 'MIT licensed',
            copyright: 'StewBeet by',
        },
    },

    fr: {
        // Navbar
        nav: {
            features: 'Fonctionnalités',
            installation: 'Installation',
            templates: 'Modèles',
            plugins: 'Plugins',
            documentation: 'Documentation',
            tools: 'Outils',
            github: 'GitHub',
            language: 'Langue',
        },

        // Hero Section
        hero: {
            versionStable: 'Version stable',
            titleLine1: 'Définissez un bloc en Python.',
            titleLine2: 'Obtenez tout le datapack.',
            description: 'StewBeet est un framework',
            beet: 'Beet',
            descriptionContinued: 'pour datapacks Minecraft. Décrivez votre contenu une fois. Modèles, recettes, tables de butin, traductions et manuel en jeu en sont tous construits à chaque compilation.',
            getStarted: 'Commencer',
            viewDocs: 'Documentation',
            codeCaption: 'definitions/additions/equipments.py',
            outputCaption: 'build/',
            outputSummary: '15 fichiers générés',
            outputNote: 'Placement, destruction, la branche Silk Touch, la recette et sa grille de craft dessinée, la génération dans le monde, les modèles et les textures. La page de manuel et les clés de traduction viennent avec.',
        },

        // In-game manual showcase
        manual: {
            title: 'Votre datapack se documente tout seul',
            description: 'Chaque objet défini obtient sa page de manuel : sa recette dessinée à partir des ingrédients déclarés, sa description, et une navigation cliquable entre catégories. Les joueurs fabriquent le livre en jeu et il est déjà à jour.',
            point1: 'Recettes dessinées depuis vos définitions, pas capturées à la main',
            point2: 'Un objet ajouté aujourd\'hui, sa page de manuel au prochain build',
            point3: 'Pages personnalisées, hooks et agencements de boutons si besoin',
            readMore: 'Comment fonctionne le manuel',
            videoFallback: 'Votre navigateur ne peut pas lire cette vidéo.',
        },

        // Features
        features: {
            title: 'Ce que vous n\'écrivez plus',
            subtitle: 'Six choses que StewBeet génère à partir de définitions que vous avez déjà écrites.',

            recipesTitle: 'Une recette, tous les systèmes de craft',
            recipesDesc: 'Déclarez une recette sur l\'objet. La recette vanilla, la recette NBT Smithed Crafter et la variante four sortent toutes de cette seule déclaration.',

            itemModelsTitle: 'Les textures deviennent des modèles sans JSON',
            itemModelsDesc: 'Déposez des PNG top, side et bottom dans assets/textures et le bloc est reconnu comme un cube. Un suffixe _on donne l\'état alimenté sans rien écrire.',

            materialsTitle: 'Un matériau, tout le palier',
            materialsDesc: 'Nommez un lingot et son équivalent vanilla. Outils, armures, minerai, blocs et pépites sont enregistrés depuis les textures déposées, recettes comprises.',

            lootTablesTitle: 'Chaque objet est donnable, tout de suite',
            lootTablesDesc: 'Chaque objet défini reçoit sa table de butin, plus une fonction _give_all qui vous remet tout le pack dans des coffres nommés pour tester.',

            langTitle: 'Les clés de traduction extraites de votre code',
            langDesc: 'Écrivez votre texte une fois en Python. en_us.json est généré depuis ce que vous avez réellement écrit, donc le fichier lang ne dérive jamais.',

            dependenciesTitle: 'Une bibliothèque manquante prévient le joueur',
            materialsImageAlt: 'Une texture de lingot, et les outils et armures enregistrés à partir d\'elle',
            materialsSnippetLabel: 'tout le palier depuis une seule entrée',
            itemModelsOnLabel: 'electric_furnace_on.json (écrit parce qu\'une texture _front_on existe)',
            recipesSnippetLabel: 'généré, compatible NBT',
            langBeforeLabel: 'ce que vous avez écrit',
            langAfterLabel: 'ce qui est construit, le texte est devenu une clé translate',
            langFileLabel: 'et les clés collectées',
            dependenciesDesc: 'StewBeet lit vos fonctions, déduit les bibliothèques réellement utilisées, les télécharge et écrit la vérification de version au runtime. S\'il en manque une, le chat la nomme, avec un lien cliquable.',
        },

        // Trust strip
        trust: {
            label: 'Activité du projet',
            releasedDaysAgo: 'publiée il y a {n} jours',
            latestRelease: 'dernière version',
            downloadsPerMonth: 'téléchargements PyPI / mois',
            publicProjects: 'projets publics qui l\'utilisent',
            githubStars: 'étoiles GitHub',
        },

        // Why StewBeet exists
        why: {
            title: 'Pourquoi ça existe',
            intro: 'Un datapack, ce n\'est pas un fichier par fonctionnalité. Ajouter un seul bloc personnalisé, c\'est écrire sa table de butin, sa définition d\'objet, son modèle, sa recette dans chaque système de craft supporté, sa clé de traduction, et ses fonctions de placement et de destruction, à la main, dans sept répertoires, dans quatre formats.',
            pain1: 'Oubliez un de ces fichiers et rien ne plante. Le bloc ne drop simplement pas, ou ne se craft pas, et vous le découvrez en jeu vingt minutes plus tard.',
            pain2: 'Renommez un objet et vous voilà à faire des rechercher-remplacer dans des centaines de fichiers JSON, en espérant que rien d\'autre ne partageait cette chaîne.',
            pain3: 'La même recette doit être écrite une fois en JSON vanilla, puis à nouveau pour chaque système de craft NBT que vous supportez, dans un format différent à chaque fois. Changez les ingrédients et vous les changez partout, sinon ça se contredit en silence.',
            resolution: 'StewBeet fait d\'une seule définition la seule chose que vous maintenez. Tous les fichiers ci-dessus en sont dérivés à chaque build, donc ils ne peuvent pas diverger. Changez les ingrédients une fois et la recette vanilla, la recette Smithed Crafter et la variante four suivent.',
            noPython: 'Pas besoin de connaître Python pour l\'utiliser. Une définition, c\'est un nom, des valeurs et une liste de recettes, plus proche d\'un formulaire à remplir que d\'un programme à écrire. Si vous savez lire un JSON de datapack, vous savez lire ça.',
            byHandTitle: 'Un bloc personnalisé, à la main',
            byHandNote: 'Huit fichiers, deux packs, quatre formats, pour un seul bloc. Oubliez-en un et rien ne plante.',
            limitsTitle: 'Là où il ne vous aidera pas',
            limitsBody: 'Il est dogmatique. L\'organisation du projet, les conventions Smithed et le pipeline de build sont des décisions que le framework a déjà prises, et travailler contre elles est plus dur que travailler sans lui. Il faut Python 3.14+ installé sur votre machine. Et si votre pack tient en quelques fonctions, les écrire à la main est vraiment le bon choix.',
        },

        // Built with StewBeet
        builtWith: {
            title: 'Fait avec StewBeet',
            subtitle: 'Du code public que vous pouvez lire, compilé avec le framework.',
            community: 'Écrits par d\'autres personnes',
            communityNote: 'Non maintenus par l\'auteur du framework',
            atScale: 'Ce qu\'il encaisse à grande échelle',
            atScaleNote: 'Les packs de l\'auteur, comptés depuis leur build',
            maintainerPacks: 'Également par l\'auteur',
            libraries: 'Bibliothèques et outils',
            integrations: 'Compatible avec les bibliothèques que vous utilisez déjà',
            integrationsNote: 'Détectées depuis votre code et fusionnées automatiquement dans le build.',
            seeAll: 'Voir la liste complète sur GitHub',
            unitSourceLines: 'lignes de Python (hors commentaires) produisent',
            itemsAlt: 'Tous les objets de {project}, tirés de son build',
            sourceLink: 'code source',
            showCount: 'afficher {n}',
            hide: 'masquer',
            unitFunctions: '.mcfunction',
            unitJson: '.json',
            unitTextures: 'textures',
            stardustDesc: 'Un gros pack de progression : paliers de minerais, blocs, tableaux et un manuel en jeu complet.',
            simplenergyDesc: 'Une bibliothèque d\'énergie et de machines dont d\'autres packs dépendent : câbles, générateurs et machines.',
        },

        // Final call to action
        finalCta: {
            title: 'Définissez un bloc. Compilez le pack.',
            subtitle: 'Le modèle Basic configure chaque plugin avec des commentaires et aucun contenu d\'exemple à supprimer.',
            action: 'Lire le guide de démarrage',
            microcopy: 'Licence MIT · Python 3.14+ · aucun compte requis',
            copyCommand: 'Copier la commande d\'installation',
            copied: 'Commande copiée',
        },

        // Installation
        installation: {
            title: 'De rien à un pack compilé en',
            titleHighlight: 'quatre commandes',
            step1: 'Installer Python',
            step1Desc: 'StewBeet demande Python 3.14 ou plus récent',
            step2: 'Installer StewBeet',
            step2Desc: 'Un pip install, dépendances comprises',
            step3: 'Initialiser le projet',
            step3Desc: 'Choisissez un modèle, obtenez un projet qui compile',
            step4: 'Compiler',
            step4Desc: 'Datapack et resource pack, zippés',
        },

        // Templates
        templates: {
            title: 'Partez d\'un modèle',
            subtitle: 'Trois points de départ. Le modèle',
            subtitleHighlight: 'Basique',
            subtitleEnd: 'est celui à prendre en cas de doute.',
            minimal: 'Minimal',
            minimalDesc: 'Un seul plugin stewbeet et rien d\'autre, pour voir ce que beet fait tout seul.',
            minimalBestFor: 'Apprendre les bases de Beet',
            basic: 'Basique',
            basicDesc: 'Tous les plugins configurés et commentés, sans contenu d\'exemple à supprimer ensuite.',
            basicBestFor: 'La plupart des utilisateurs (recommandé)',
            extensive: 'Complet',
            extensiveDesc: 'Un projet qui tourne et utilise tout : paliers de minerai, blocs personnalisés, peintures, manuel.',
            extensiveBestFor: 'Lire de vrais exemples',
            recommended: 'Recommandé',
            downloadZip: 'ou télécharger le .zip',
            tipTitle: 'Lequel choisir ?',
            tipBody: 'Prenez le modèle Basique. Il branche tous les plugins avec une configuration commentée et aucun contenu d\'exemple, vous n\'ajoutez que ce dont votre projet a besoin.',
        },

        // Showcase / plugins listing
        showcase: {
            subtitle: 'Chaque étape du build est un plugin que vous pouvez activer, désactiver ou remplacer.',
            legend: 'Légende :',
            fullyDependent: 'Entièrement dépendant',
            partlyDependent: 'Partiellement dépendant',
            independent: 'Indépendant',
        },

        // Plugins Table
        pluginsTable: {
            category: 'Catégorie',
            plugin: 'Plugin',
            description: 'Description',
            image: 'Image',
            dependency: 'Dépendance',
            // Categories
            categoryCore: 'Noyau',
            categoryResourcePack: 'Pack de Ressources',
            categoryRecipes: 'Recettes',
            categoryCustomContent: 'Contenu Personnalisé',
            categoryDocumentation: 'Documentation',
            categoryDatapack: 'Datapack',
            categoryFinalization: 'Finalisation',
            categoryAutomation: 'Automatisation',
            categoryBuild: 'Construction',
            categoryCompatibility: 'Compatibilité',
            // Plugins
            initializeDesc: 'Initialise le framework et configure les métadonnées du projet',
            verifyDefinitionsDesc: 'Valide la structure des définitions et vérifie la cohérence',
            soundsDesc: 'Traite les fichiers audio et génère sounds.json automatiquement',
            itemModelsDesc: 'Génère automatiquement les modèles d\'objets et de blocs',
            checkPowerOf2Desc: 'Valide que les textures utilisent des résolutions en puissance de 2',
            customRecipesDesc: 'Génère des recettes vanilla, smithed, furnace et pulverizer',
            customPaintingsDesc: 'Crée des variantes de peintures personnalisées',
            ingameManualDesc: 'Génère un manuel interactif en jeu avec documentation',
            loadingDesc: 'Configure le système de chargement avec versioning',
            customBlocksDesc: 'Implémente le placement, la destruction et l\'interaction pour les blocs personnalisés',
            lootTablesDesc: 'Génère les tables de butin et la fonctionnalité give-all',
            sortersDesc: 'Génère des fonctions de tri pour les listes NBT',
            simpledrawerDesc: 'Ajoute la compatibilité matériaux SimpleDrawer pour les tiroirs compactés',
            neoEnchantDesc: 'Fournit la compatibilité veinminer NeoEnchant pour les minerais personnalisés',
            customBlocksTickingDesc: 'Configure le système de ticking pour les blocs personnalisés',
            basicDatapackStructureDesc: 'Crée la structure temporelle (tick, seconde, minute)',
            dependenciesDesc: 'Gère les dépendances de bibliothèques externes',
            checkUnusedTexturesDesc: 'Identifie les textures inutilisées dans le pack de ressources',
            langFileDesc: 'Génère automatiquement les fichiers de langue',
            headersDesc: 'Ajoute des en-têtes automatiques aux fichiers mcfunction',
            scoreboardConstantsDesc: 'Détecte les constantes de scoreboard et génère leurs commandes d\'initialisation',
            archiveDesc: 'Crée des archives zip des datapacks et packs de ressources',
            mergeSmithedWeldDesc: 'Fusionne les datapacks et packs de ressources avec les bibliothèques',
            copyToDestinationDesc: 'Copie les packs générés vers les dossiers de destination',
            livereloadDesc: 'Rechargement /reload automatique en jeu à chaque build (link ou destinations)',
            computeSha1Desc: 'Calcule les hachages SHA1 pour tous les fichiers zip',
        },

        // Documentation Page
        documentation: {
            title: 'Documentation',
            subtitle: 'Apprenez à utiliser StewBeet',
            cookbook: 'Recettes',
            cookbookDesc: 'Des fichiers complets et fonctionnels, à lire de bout en bout.',
            helperReference: 'Référence des fonctions utilitaires',
            helperReferenceDesc: 'Chaque helper que StewBeet ajoute pour écrire des fichiers, et ses arguments.',
            quickstart: 'Démarrage rapide',
            quickstartDesc: 'Trois commandes, de rien à un datapack chargeable.',
            gettingStarted: 'Tutoriel : votre premier datapack',
            groupStart: 'Commencer ici',
            groupStartDesc: 'Installez le framework et construisez un pack complet de bout en bout.',
            groupGuides: 'Guides',
            groupGuidesDesc: 'Une tâche par guide, dans l\'ordre où vous les rencontrez.',
            groupReference: 'Référence',
            groupReferenceDesc: 'À consulter : API, options et fichiers générés.',
            gettingStartedDesc: 'Guide complet pour débutants - installation, configuration et création de votre premier datapack',
            definitionsSetup: 'Définir objets et blocs',
            definitionsSetupDesc: 'Apprenez à définir des objets, blocs et configurations d\'équipement personnalisés',
            writingToFiles: 'Écriture dans les Fichiers',
            writingToFilesDesc: 'Maîtrisez l\'écriture de fichiers avec le chargement statique, l\'API native de beet et les fonctions d\'aide de StewBeet',
            beetConfig: 'Configurer le build',
            beetConfigDesc: 'Référence complète pour toutes les options de configuration beet.yml incluant les paramètres spécifiques à StewBeet',
            equations: 'Équations',
            equationsDesc: 'Constructeurs chaînables Equation qui compilent en commandes scoreboard Minecraft',
            dependencies: 'Utiliser des bibliothèques',
            dependenciesDesc: 'Déclarez des dépendances de bibliothèques et générez automatiquement des vérifications de version au runtime',
            continuousDelivery: 'Publier automatiquement',
            continuousDeliveryDesc: 'Publiez des releases sur GitHub, Modrinth, Smithed et PlanetMinecraft en une seule commande',
            ingameManual: 'Manuel en jeu',
            ingameManualDesc: 'Générez un manuel en jeu extensible et orienté dialogue avec pages personnalisées, hooks et agencements de boutons',
            plugins: 'Plugins Disponibles',
            comingSoon: 'D\'autres guides sont en cours d\'écriture.',
            searchPlaceholder: 'Rechercher des plugins...',
            filterAll: 'Tous',
            filterCore: 'Core',
            filterCompatibility: 'Compatibilité',
            filterDatapack: 'Datapack',
            pluginName: 'Plugin',
            description: 'Description',
            noResults: 'Aucun plugin trouvé correspondant à votre recherche.',
        },

        // Markdown Page
        markdown: {
            back: 'Retour',
            contents: 'Contenu',
            viewOnGithub: 'Voir sur GitHub',
            error: 'Erreur',
            loading: 'Chargement...',
            noPlugin: 'Aucun plugin spécifié. Veuillez fournir un paramètre "src".',
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
            title: 'Outils',
            subtitle: 'Outils utiles pour StewBeet et le développement de datapacks Minecraft',
            markdownToBBCode: 'Convertisseur Markdown vers BBCode',
            markdownToBBCodeDesc: 'Convertissez du texte Markdown en format BBCode pour publier sur PlanetMinecraft. Supporte les badges, listes, tableaux, blocs de code, spoilers et plus.',
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
            tagline: 'Un framework Beet qui transforme des définitions Python en datapacks et resource packs finis.',
            community: 'Communauté',
            resources: 'Ressources',
            github: 'GitHub',
            discord: 'Discord',
            youtube: 'YouTube',
            pypiPackage: 'Package PyPI',
            planetMinecraft: 'PlanetMinecraft',
            reportBug: 'Signaler un Bug',
            license: 'Licence MIT',
            copyright: 'StewBeet par',
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
