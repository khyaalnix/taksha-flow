#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the release type from argument
RELEASE_TYPE=${1:-beta}

# Validate release type
if [[ ! "$RELEASE_TYPE" =~ ^(beta|alpha|rc|prod)$ ]]; then
  echo -e "${RED}Error: Invalid release type '$RELEASE_TYPE'${NC}"
  echo "Usage: $0 [beta|alpha|rc|prod]"
  exit 1
fi

# Get current version from package.json
CURRENT_VERSION=$(node -p "require('./package.json').version")
echo -e "${BLUE}Current version: $CURRENT_VERSION${NC}"

# Parse version components
IFS='.' read -ra VERSION_PARTS <<< "$CURRENT_VERSION"
MAJOR=${VERSION_PARTS[0]}
MINOR=${VERSION_PARTS[1]}
PATCH=${VERSION_PARTS[2]%%.*}

# Generate new version based on release type
case $RELEASE_TYPE in
  "prod")
    # For production, use current version or bump patch
    NEW_VERSION="$MAJOR.$MINOR.$PATCH"
    TAG_PREFIX="v"
    ;;
  "beta")
    # Find the latest beta number
    LATEST_TAG=$(git tag -l "v$MAJOR.$MINOR.$PATCH.beta.*" | sort -V | tail -n1)
    if [ -z "$LATEST_TAG" ]; then
      LATEST_BETA=0
    else
      LATEST_BETA=$(echo "$LATEST_TAG" | sed 's/.*\.beta\.//')
    fi
    NEXT_BETA=$((LATEST_BETA + 1))
    NEW_VERSION="$MAJOR.$MINOR.$PATCH.beta.$NEXT_BETA"
    TAG_PREFIX="v"
    ;;
  "alpha")
    # Find the latest alpha number
    LATEST_TAG=$(git tag -l "v$MAJOR.$MINOR.$PATCH.alpha.*" | sort -V | tail -n1)
    if [ -z "$LATEST_TAG" ]; then
      LATEST_ALPHA=0
    else
      LATEST_ALPHA=$(echo "$LATEST_TAG" | sed 's/.*\.alpha\.//')
    fi
    NEXT_ALPHA=$((LATEST_ALPHA + 1))
    NEW_VERSION="$MAJOR.$MINOR.$PATCH.alpha.$NEXT_ALPHA"
    TAG_PREFIX="v"
    ;;
  "rc")
    # Find the latest rc number
    LATEST_TAG=$(git tag -l "v$MAJOR.$MINOR.$PATCH.rc.*" | sort -V | tail -n1)
    if [ -z "$LATEST_TAG" ]; then
      LATEST_RC=0
    else
      LATEST_RC=$(echo "$LATEST_TAG" | sed 's/.*\.rc\.//')
    fi
    NEXT_RC=$((LATEST_RC + 1))
    NEW_VERSION="$MAJOR.$MINOR.$PATCH.rc.$NEXT_RC"
    TAG_PREFIX="v"
    ;;
esac

TAG_NAME="${TAG_PREFIX}${NEW_VERSION}"

echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}  Frontend Deployment${NC}"
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}Release Type:${NC} $RELEASE_TYPE"
echo -e "${BLUE}New Version:${NC}  $NEW_VERSION"
echo -e "${BLUE}Tag Name:${NC}     $TAG_NAME"
echo -e "${YELLOW}═══════════════════════════════════════════${NC}"
echo ""

# Confirmation prompt
read -p "Do you want to create and push this tag? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo -e "${RED}Deployment cancelled.${NC}"
  exit 1
fi

# Check if tag already exists
if git rev-parse "$TAG_NAME" >/dev/null 2>&1; then
  echo -e "${RED}Error: Tag $TAG_NAME already exists!${NC}"
  exit 1
fi

# Check for uncommitted changes
if [[ -n $(git status -s) ]]; then
  echo -e "${YELLOW}Warning: You have uncommitted changes.${NC}"
  read -p "Do you want to continue? (y/N) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}Deployment cancelled.${NC}"
    exit 1
  fi
fi

# Create the tag
echo -e "${BLUE}Creating tag $TAG_NAME...${NC}"
git tag -a "$TAG_NAME" -m "Release $TAG_NAME - Frontend $RELEASE_TYPE deployment"

# Push the tag
echo -e "${BLUE}Pushing tag to origin...${NC}"
git push origin "$TAG_NAME"

echo ""
echo -e "${GREEN}✅ Tag $TAG_NAME created and pushed successfully!${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. GitHub Actions workflow will automatically deploy to GitHub Pages"
echo "2. Check the workflow status: https://github.com/khyaalnix/taksha-flow/actions"
echo "3. Once deployed, visit: https://khyaalnix.github.io/flow"
echo ""
echo -e "${BLUE}Monitor deployment:${NC}"
echo "   git tag -l 'v*' | tail -5    # View recent tags"
echo "   git tag -d $TAG_NAME          # Delete local tag (if needed)"
echo "   git push --delete origin $TAG_NAME  # Delete remote tag (if needed)"
