#!/usr/bin/env python
# coding: utf-8

# # Graphviz Examples
# 
# ## 1. Introduction
# 
# ### 1.1 Links
# 
# - [Dot Language](https://graphviz.gitlab.io/_pages/doc/info/lang.html)
# 

# In[1]:


try:
    import graphviz
except:
    get_ipython().system('brew install graphviz')
    get_ipython().system('pip install graphviz')
    import graphviz


# In[2]:


g = graphviz.Digraph('G', filename='graphviz.gv')
g.edge('A', 'O', label='1')
g.edge('B', 'O', label='2')
g.edge('C', 'O', label='3')
print(g.source)


# In[3]:


graphviz.Source(g.source)


# In[4]:


graphviz.Source('''digraph G { A->B->C } ''')


# In[5]:


graphviz.Source('''digraph G { rankdir="LR" A->B->C } ''')


# In[6]:


graphviz.Source('''digraph G { rankdir="LR" B[shape=box3d] A->B->C } ''')


# In[7]:


graphviz.Source('''digraph G { rankdir="LR" B[shape=box3d width=0.7 height=0.5] A->B->C } ''')

